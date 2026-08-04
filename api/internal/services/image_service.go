package services

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/your-app/internal/models"
)

// ImageService defines the interface for image fetching
type ImageService interface {
	GetImages(ctx context.Context) ([]models.ImageInfo, error)
	GetImagesJSON(ctx context.Context) (string, error)
	GetVillaPageData(ctx context.Context, title, activePage string) (*models.VillaPageData, error)
	ClearCache()
	GetCacheStatus() map[string]interface{}
}

// BaseImageService provides common functionality
type BaseImageService struct {
	Config models.ImageServiceConfig
	Cache  *models.ImageCache
}

// NewBaseImageService creates a new base image service
func NewBaseImageService(config models.ImageServiceConfig) *BaseImageService {
	return &BaseImageService{
		Config: config,
		Cache: &models.ImageCache{
			Images:    []models.ImageInfo{},
			UpdatedAt: time.Now(),
			TTL:       config.CacheTTL,
		},
	}
}

// ClearCache clears the image cache
func (s *BaseImageService) ClearCache() {
	s.Cache.Images = []models.ImageInfo{}
	s.Cache.UpdatedAt = time.Now()
}

// GetCacheStatus returns cache status
func (s *BaseImageService) GetCacheStatus() map[string]interface{} {
	return map[string]interface{}{
		"image_count": len(s.Cache.Images),
		"updated_at":  s.Cache.UpdatedAt,
		"ttl":         s.Cache.TTL,
		"is_expired":  s.Cache.IsExpired(),
		"use_local":   s.Config.UseLocal,
		"s3_bucket":   s.Config.S3Bucket,
	}
}
