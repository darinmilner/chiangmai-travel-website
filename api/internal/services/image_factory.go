package services

import (
	"log"
	"os"
	"time"

	"api/internal/models"
)

// ImageServiceFactory creates the appropriate image service
type ImageServiceFactory struct{}

// NewImageServiceFactory creates a new factory
func NewImageServiceFactory() *ImageServiceFactory {
	return &ImageServiceFactory{}
}

// CreateService creates an image service based on configuration
func (f *ImageServiceFactory) CreateService(config models.ImageServiceConfig) (ImageService, error) {
	// Set defaults
	if config.CacheTTL == 0 {
		config.CacheTTL = 5 * time.Minute
	}
	if config.S3Prefix == "" {
		config.S3Prefix = "villa/"
	}

	// Check if we should use local
	useLocal := config.UseLocal || os.Getenv("USE_LOCAL_IMAGES") == "true"

	// Check if we have S3 credentials
	hasS3Creds := config.S3Bucket != "" && os.Getenv("AWS_ACCESS_KEY_ID") != ""

	if useLocal || !hasS3Creds {
		log.Println("Using local image service")
		if config.LocalImageDir == "" {
			config.LocalImageDir = "static/images/villa"
		}
		return NewLocalImageService(config), nil
	}

	log.Printf("Using S3 image service with bucket: %s", config.S3Bucket)
	return NewS3ImageService(config)
}
