package services

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"path/filepath"
	"strings"
	"time"

	"api/internal/models"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/config"
	"github.com/aws/aws-sdk-go-v2/service/s3"
)

// S3ImageService handles fetching images from S3
// NOTE: Image processing is now handled by Lambda, not in the Go app
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

			// Skip processed images - they're handled by Lambda
			if shouldSkipImage(key) {
				continue
			}

			// Get image info using Lambda-generated variants
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

// getImageInfo creates ImageInfo from S3 object key
// Uses Lambda-generated variants
func (s *S3ImageService) getImageInfo(key string) *models.ImageInfo {
	// Extract base name without extension and prefix
	baseName := strings.TrimPrefix(key, s.Config.S3Prefix)
	baseName = strings.TrimSuffix(baseName, filepath.Ext(baseName))

	// Clean up the name
	baseName = strings.TrimSuffix(baseName, ".jpg")
	baseName = strings.TrimSuffix(baseName, ".jpeg")
	baseName = strings.TrimSuffix(baseName, ".png")
	baseName = strings.TrimSuffix(baseName, ".webp")

	// Build URLs - Lambda has already created the processed versions
	var fullURL, thumbURL, mediumURL string

	if s.Config.CloudFrontURL != "" {
		// Use CloudFront for delivery
		fullURL = fmt.Sprintf("%s/%s", s.Config.CloudFrontURL, key)
		thumbURL = fmt.Sprintf("%s/%sthumb_%s.jpg", s.Config.CloudFrontURL, s.Config.S3Prefix, baseName)
		mediumURL = fmt.Sprintf("%s/%smedium_%s.jpg", s.Config.CloudFrontURL, s.Config.S3Prefix, baseName)

		// Also support WebP if available
		webpURL := fmt.Sprintf("%s/%s%s.webp", s.Config.CloudFrontURL, s.Config.S3Prefix, baseName)
		// Check if WebP exists (optional)
		// Could add a head request here, but skip for performance

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
		Width:  1200, // Could fetch from metadata
		Height: 800,
	}
}
