package services

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"path/filepath"
	"strings"
	"time"

	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
	"github.com/aws/aws-sdk-go-v2/service/s3/types"
	"github.com/your-app/internal/models"
)

// S3ImageService handles fetching images from S3
type S3ImageService struct {
	*BaseImageService
	S3Client *s3.Client
}

// NewS3ImageService creates a new S3 image service
func NewS3ImageService(config models.ImageServiceConfig) (*S3ImageService, error) {
	if config.S3Bucket == "" {
		return nil, fmt.Errorf("S3 bucket name is required")
	}

	// Load AWS config
	cfg, err := config.LoadDefaultConfig(context.Background(),
		config.WithRegion(config.S3Region),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to load AWS config: %v", err)
	}

	// Create S3 client
	client := s3.NewFromConfig(cfg)

	return &S3ImageService{
		BaseImageService: NewBaseImageService(config),
		S3Client:         client,
	}, nil
}

// GetImages retrieves images from S3
func (s *S3ImageService) GetImages(ctx context.Context) ([]models.ImageInfo, error) {
	// Check cache
	if s.Config.EnableCache && len(s.Cache.Images) > 0 && !s.Cache.IsExpired() {
		log.Printf("Returning %d images from cache", len(s.Cache.Images))
		return s.Cache.Images, nil
	}

	log.Printf("Fetching images from S3 bucket: %s", s.Config.S3Bucket)

	// List objects in S3
	var images []models.ImageInfo
	var continuationToken *string

	for {
		input := &s3.ListObjectsV2Input{
			Bucket:            aws.String(s.Config.S3Bucket),
			Prefix:            aws.String(s.Config.S3Prefix),
			ContinuationToken: continuationToken,
		}

		result, err := s.S3Client.ListObjectsV2(ctx, input)
		if err != nil {
			return nil, fmt.Errorf("failed to list objects: %v", err)
		}

		for _, obj := range result.Contents {
			key := aws.ToString(obj.Key)

			// Skip processed images and non-images
			if shouldSkipImage(key) {
				continue
			}

			// Get image info
			info := s.getImageInfo(key)
			if info != nil {
				images = append(images, *info)
			}
		}

		if result.IsTruncated == nil || !*result.IsTruncated {
			break
		}
		continuationToken = result.NextContinuationToken
	}

	// Update cache
	if s.Config.EnableCache {
		s.Cache.Images = images
		s.Cache.UpdatedAt = time.Now()
	}

	log.Printf("Retrieved %d images from S3", len(images))
	return images, nil
}

// GetImagesJSON returns images as JSON string
func (s *S3ImageService) GetImagesJSON(ctx context.Context) (string, error) {
	images, err := s.GetImages(ctx)
	if err != nil {
		return "", err
	}

	jsonData, err := json.Marshal(images)
	if err != nil {
		return "", fmt.Errorf("failed to marshal images to JSON: %v", err)
	}

	return string(jsonData), nil
}

// GetVillaPageData returns data for the villa page
func (s *S3ImageService) GetVillaPageData(ctx context.Context, title, activePage string) (*models.VillaPageData, error) {
	images, err := s.GetImages(ctx)
	if err != nil {
		return nil, err
	}

	imagesJSON, err := json.Marshal(images)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal images: %v", err)
	}

	return &models.VillaPageData{
		Title:      title,
		ActivePage: activePage,
		Images:     images,
		ImagesJSON: string(imagesJSON),
	}, nil
}

// getImageInfo creates ImageInfo from S3 object key
func (s *S3ImageService) getImageInfo(key string) *models.ImageInfo {
	// Extract base name without extension and prefix
	baseName := strings.TrimPrefix(key, s.Config.S3Prefix)
	baseName = strings.TrimSuffix(baseName, filepath.Ext(baseName))

	// Clean up the name
	baseName = strings.TrimSuffix(baseName, ".jpg")
	baseName = strings.TrimSuffix(baseName, ".jpeg")
	baseName = strings.TrimSuffix(baseName, ".png")
	baseName = strings.TrimSuffix(baseName, ".webp")

	// Build URLs
	var fullURL, thumbURL, mediumURL string

	if s.Config.CloudFrontURL != "" {
		// Use CloudFront for delivery
		fullURL = fmt.Sprintf("%s/%s", s.Config.CloudFrontURL, key)
		thumbURL = fmt.Sprintf("%s/%sthumb_%s.jpg", s.Config.CloudFrontURL, s.Config.S3Prefix, baseName)
		mediumURL = fmt.Sprintf("%s/%smedium_%s.jpg", s.Config.CloudFrontURL, s.Config.S3Prefix, baseName)
	} else {
		// Use S3 direct
		fullURL = fmt.Sprintf("https://%s.s3.%s.amazonaws.com/%s",
			s.Config.S3Bucket, s.Config.S3Region, key)
		thumbURL = fmt.Sprintf("https://%s.s3.%s.amazonaws.com/%sthumb_%s.jpg",
			s.Config.S3Bucket, s.Config.S3Region, s.Config.S3Prefix, baseName)
		mediumURL = fmt.Sprintf("https://%s.s3.%s.amazonaws.com/%smedium_%s.jpg",
			s.Config.S3Bucket, s.Config.S3Region, s.Config.S3Prefix, baseName)
	}

	return &models.ImageInfo{
		Full:   fullURL,
		Thumb:  thumbURL,
		Medium: mediumURL,
		Alt:    strings.ReplaceAll(baseName, "-", " "),
		Width:  1200, // Could get from metadata if available
		Height: 800,
	}
}

// shouldSkipImage checks if an image should be skipped
func shouldSkipImage(key string) bool {
	// Skip processed versions
	skipPatterns := []string{"thumb_", "medium_", "carousel_", "_thumb", "_medium", "_carousel"}
	for _, pattern := range skipPatterns {
		if strings.Contains(key, pattern) {
			return true
		}
	}

	// Skip non-image files
	ext := strings.ToLower(filepath.Ext(key))
	validExts := []string{".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif"}
	for _, validExt := range validExts {
		if ext == validExt {
			return false
		}
	}

	return true
}
