package services

import (
	"os"
	"testing"

	"api/internal/models"
)

func TestImageServiceFactory_CreateService(t *testing.T) {
	factory := NewImageServiceFactory()

	t.Run("should create local service when USE_LOCAL_IMAGES is true", func(t *testing.T) {
		os.Setenv("USE_LOCAL_IMAGES", "true")
		defer os.Unsetenv("USE_LOCAL_IMAGES")

		config := models.ImageServiceConfig{
			LocalImageDir: "/tmp/test-images",
		}

		service, err := factory.CreateService(config)
		if err != nil {
			t.Fatalf("Failed to create service: %v", err)
		}

		_, ok := service.(*LocalImageService)
		if !ok {
			t.Error("Expected LocalImageService, got different type")
		}
	})

	t.Run("should create local service when no S3 credentials", func(t *testing.T) {
		os.Setenv("AWS_ACCESS_KEY_ID", "")
		defer os.Unsetenv("AWS_ACCESS_KEY_ID")

		config := models.ImageServiceConfig{
			LocalImageDir: "/tmp/test-images",
		}

		service, err := factory.CreateService(config)
		if err != nil {
			t.Fatalf("Failed to create service: %v", err)
		}

		_, ok := service.(*LocalImageService)
		if !ok {
			t.Error("Expected LocalImageService when no S3 credentials")
		}
	})

	t.Run("should create S3 service when configured", func(t *testing.T) {
		// Skip if no S3 credentials
		if os.Getenv("AWS_ACCESS_KEY_ID") == "" {
			t.Skip("No S3 credentials, skipping S3 test")
		}

		config := models.ImageServiceConfig{
			S3Bucket:      "test-bucket",
			S3Region:      "us-east-1",
			UseLocal:      false,
			LocalImageDir: "/tmp/test-images",
		}

		service, err := factory.CreateService(config)
		if err != nil {
			t.Fatalf("Failed to create service: %v", err)
		}

		_, ok := service.(*S3ImageService)
		if !ok {
			t.Error("Expected S3ImageService, got different type")
		}
	})
}
