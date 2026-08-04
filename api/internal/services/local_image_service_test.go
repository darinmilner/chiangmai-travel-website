package services

import (
	"context"
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
	"time"

	"github.com/your-app/internal/models"
)

func TestLocalImageService_GetImages(t *testing.T) {
	config := SetupTestEnvironment(t)
	if config == nil {
		return
	}

	t.Run("should return images from local directory", func(t *testing.T) {
		// Create test images
		testImages := []string{
			"exterior.jpg",
			"pool.jpg",
			"living-room.jpg",
		}
		CreateTestImages(t, config.ImageDir, testImages)

		// Create service
		serviceConfig := models.ImageServiceConfig{
			LocalImageDir: config.ImageDir,
			UseLocal:      true,
			EnableCache:   false,
		}
		service := NewLocalImageService(serviceConfig)

		// Get images
		ctx := context.Background()
		images, err := service.GetImages(ctx)
		if err != nil {
			t.Fatalf("Failed to get images: %v", err)
		}

		// Verify
		if len(images) != len(testImages) {
			t.Errorf("Expected %d images, got %d", len(testImages), len(images))
		}

		for i, img := range images {
			if img.Full == "" {
				t.Errorf("Image %d has empty Full URL", i)
			}
			if img.Alt == "" {
				t.Errorf("Image %d has empty Alt text", i)
			}
		}
	})

	t.Run("should handle empty directory", func(t *testing.T) {
		// Create empty directory
		emptyDir := filepath.Join(config.TempDir, "empty")
		if err := os.MkdirAll(emptyDir, 0755); err != nil {
			t.Fatalf("Failed to create empty dir: %v", err)
		}

		serviceConfig := models.ImageServiceConfig{
			LocalImageDir: emptyDir,
			UseLocal:      true,
			EnableCache:   false,
		}
		service := NewLocalImageService(serviceConfig)

		ctx := context.Background()
		images, err := service.GetImages(ctx)
		if err != nil {
			t.Fatalf("Failed to get images: %v", err)
		}

		if len(images) != 0 {
			t.Errorf("Expected 0 images, got %d", len(images))
		}
	})

	t.Run("should only include valid image extensions", func(t *testing.T) {
		// Create mixed files
		files := []string{
			"image1.jpg",
			"image2.png",
			"image3.webp",
			"document.txt",
			"video.mp4",
		}
		CreateTestImages(t, config.ImageDir, files)

		serviceConfig := models.ImageServiceConfig{
			LocalImageDir: config.ImageDir,
			UseLocal:      true,
			EnableCache:   false,
		}
		service := NewLocalImageService(serviceConfig)

		ctx := context.Background()
		images, err := service.GetImages(ctx)
		if err != nil {
			t.Fatalf("Failed to get images: %v", err)
		}

		// Should only include image files
		expectedCount := 3 // jpg, png, webp
		if len(images) != expectedCount {
			t.Errorf("Expected %d images, got %d", expectedCount, len(images))
		}
	})

	t.Run("should skip processed images", func(t *testing.T) {
		// Create original and processed images
		files := []string{
			"exterior.jpg",
			"thumb_exterior.jpg",
			"medium_exterior.jpg",
			"carousel_exterior.jpg",
		}
		CreateTestImages(t, config.ImageDir, files)

		serviceConfig := models.ImageServiceConfig{
			LocalImageDir: config.ImageDir,
			UseLocal:      true,
			EnableCache:   false,
		}
		service := NewLocalImageService(serviceConfig)

		ctx := context.Background()
		images, err := service.GetImages(ctx)
		if err != nil {
			t.Fatalf("Failed to get images: %v", err)
		}

		// Should only include original image
		if len(images) != 1 {
			t.Errorf("Expected 1 image, got %d", len(images))
		}

		if len(images) > 0 && images[0].Full == "" {
			t.Error("Image Full URL is empty")
		}
	})
}

func TestLocalImageService_Caching(t *testing.T) {
	config := SetupTestEnvironment(t)
	if config == nil {
		return
	}

	t.Run("should use cache when enabled", func(t *testing.T) {
		// Create test images
		testImages := []string{"test1.jpg", "test2.jpg"}
		CreateTestImages(t, config.ImageDir, testImages)

		serviceConfig := models.ImageServiceConfig{
			LocalImageDir: config.ImageDir,
			UseLocal:      true,
			EnableCache:   true,
			CacheTTL:      10 * time.Minute,
		}
		service := NewLocalImageService(serviceConfig)

		ctx := context.Background()

		// First call should populate cache
		images1, err := service.GetImages(ctx)
		if err != nil {
			t.Fatalf("First call failed: %v", err)
		}

		// Second call should use cache
		images2, err := service.GetImages(ctx)
		if err != nil {
			t.Fatalf("Second call failed: %v", err)
		}

		if len(images1) != len(images2) {
			t.Errorf("Cache mismatch: got %d vs %d", len(images1), len(images2))
		}

		// Check cache status
		status := service.GetCacheStatus()
		if status["image_count"] != len(testImages) {
			t.Errorf("Cache count mismatch: expected %d, got %d", len(testImages), status["image_count"])
		}
	})

	t.Run("should clear cache", func(t *testing.T) {
		// Create test images
		testImages := []string{"clear1.jpg", "clear2.jpg"}
		CreateTestImages(t, config.ImageDir, testImages)

		serviceConfig := models.ImageServiceConfig{
			LocalImageDir: config.ImageDir,
			UseLocal:      true,
			EnableCache:   true,
		}
		service := NewLocalImageService(serviceConfig)

		ctx := context.Background()

		// Populate cache
		_, err := service.GetImages(ctx)
		if err != nil {
			t.Fatalf("Failed to get images: %v", err)
		}

		// Clear cache
		service.ClearCache()

		// Check cache is empty
		status := service.GetCacheStatus()
		if status["image_count"] != 0 {
			t.Errorf("Cache should be empty, got %d", status["image_count"])
		}

		// Should fetch fresh
		images, err := service.GetImages(ctx)
		if err != nil {
			t.Fatalf("Failed to get images after clear: %v", err)
		}

		if len(images) == 0 {
			t.Error("Should have images after cache clear")
		}
	})
}

func TestLocalImageService_GetImagesJSON(t *testing.T) {
	config := SetupTestEnvironment(t)
	if config == nil {
		return
	}

	t.Run("should return valid JSON", func(t *testing.T) {
		// Create test images
		testImages := []string{"test1.jpg", "test2.jpg"}
		CreateTestImages(t, config.ImageDir, testImages)

		serviceConfig := models.ImageServiceConfig{
			LocalImageDir: config.ImageDir,
			UseLocal:      true,
			EnableCache:   false,
		}
		service := NewLocalImageService(serviceConfig)

		ctx := context.Background()
		jsonData, err := service.GetImagesJSON(ctx)
		if err != nil {
			t.Fatalf("Failed to get images JSON: %v", err)
		}

		// Verify JSON is valid
		var images []models.ImageInfo
		if err := json.Unmarshal([]byte(jsonData), &images); err != nil {
			t.Fatalf("Invalid JSON: %v", err)
		}

		if len(images) == 0 {
			t.Error("Expected at least one image in JSON")
		}
	})
}

func TestLocalImageService_GetVillaPageData(t *testing.T) {
	config := SetupTestEnvironment(t)
	if config == nil {
		return
	}

	t.Run("should return complete page data", func(t *testing.T) {
		// Create test images
		testImages := []string{"page1.jpg", "page2.jpg"}
		CreateTestImages(t, config.ImageDir, testImages)

		serviceConfig := models.ImageServiceConfig{
			LocalImageDir: config.ImageDir,
			UseLocal:      true,
			EnableCache:   false,
		}
		service := NewLocalImageService(serviceConfig)

		ctx := context.Background()
		title := "Test Villa"
		activePage := "villa"

		data, err := service.GetVillaPageData(ctx, title, activePage)
		if err != nil {
			t.Fatalf("Failed to get page data: %v", err)
		}

		if data.Title != title {
			t.Errorf("Title mismatch: expected %s, got %s", title, data.Title)
		}

		if data.ActivePage != activePage {
			t.Errorf("ActivePage mismatch: expected %s, got %s", activePage, data.ActivePage)
		}

		if len(data.Images) == 0 {
			t.Error("Expected at least one image in page data")
		}

		if data.ImagesJSON == "" {
			t.Error("ImagesJSON should not be empty")
		}
	})
}
