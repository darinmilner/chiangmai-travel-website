package services

import (
	"context"
	"fmt"
	"log"
	"path/filepath"
	"strings"
	"time"

	"api/internal/models"
	"github.com/aws/aws-sdk-go-v2/aws"
	"github.com/aws/aws-sdk-go-v2/service/s3"
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

	// For now, return a service without AWS SDK (will be implemented later)
	// This avoids the config.LoadDefaultConfig issue
	return &S3ImageService{
		BaseImageService: NewBaseImageService(config),
		S3Client:         nil, // Will be initialized when AWS SDK is properly configured
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

	// If S3 client is not initialized, fallback to local or return error
	if s.S3Client == nil {
		log.Printf("S3 client not initialized, using local fallback")
		return s.getFallbackImages(), nil
	}

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

			// Skip processed images
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

	// Convert to JSON manually
	result := "["
	for i, img := range images {
		if i > 0 {
			result += ","
		}
		result += fmt.Sprintf(`{"full":"%s","thumb":"%s","medium":"%s","alt":"%s","width":%d,"height":%d}`,
			img.Full, img.Thumb, img.Medium, img.Alt, img.Width, img.Height)
	}
	result += "]"

	return result, nil
}

// GetVillaPageData returns data for the villa page
func (s *S3ImageService) GetVillaPageData(ctx context.Context, title, activePage string) (*models.VillaPageData, error) {
	images, err := s.GetImages(ctx)
	if err != nil {
		return nil, err
	}

	imagesJSON, err := s.GetImagesJSON(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal images: %v", err)
	}

	return &models.VillaPageData{
		Title:      title,
		ActivePage: activePage,
		Images:     images,
		ImagesJSON: imagesJSON,
	}, nil
}

// getFallbackImages returns default images
func (s *S3ImageService) getFallbackImages() []models.ImageInfo {
	fallbacks := []string{
		"/static/images/villa/exterior.jpg",
		"/static/images/villa/pool.jpg",
		"/static/images/villa/living-room.jpg",
		"/static/images/villa/kitchen.jpg",
		"/static/images/villa/bedroom.jpg",
		"/static/images/villa/garden.jpg",
	}

	var images []models.ImageInfo
	for _, path := range fallbacks {
		baseName := strings.TrimSuffix(filepath.Base(path), filepath.Ext(path))
		images = append(images, models.ImageInfo{
			Full:   path,
			Thumb:  path,
			Medium: path,
			Alt:    strings.ReplaceAll(baseName, "-", " "),
			Width:  1200,
			Height: 800,
		})
	}
	return images
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
		Width:  1200,
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
