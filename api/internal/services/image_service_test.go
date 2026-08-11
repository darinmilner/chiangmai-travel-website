package services

import (
	"testing"
	"time"

	"api/internal/models"
)

// TestImageServiceInterface ensures implementations satisfy the interface
func TestImageServiceInterface(t *testing.T) {
	var _ ImageService = (*LocalImageService)(nil)
	var _ ImageService = (*S3ImageService)(nil)
}

// TestBaseImageService tests common functionality
func TestBaseImageService(t *testing.T) {
	t.Run("should initialize with config", func(t *testing.T) {
		config := models.ImageServiceConfig{
			UseLocal:    true,
			EnableCache: true,
			CacheTTL:    5 * time.Minute,
		}

		service := NewBaseImageService(config)

		if service.Config.UseLocal != true {
			t.Error("UseLocal should be true")
		}

		if service.Config.EnableCache != true {
			t.Error("EnableCache should be true")
		}

		if service.Cache.TTL != 5*time.Minute {
			t.Errorf("Cache TTL mismatch: expected 5m, got %v", service.Cache.TTL)
		}
	})

	t.Run("should clear cache", func(t *testing.T) {
		config := models.ImageServiceConfig{
			EnableCache: true,
		}

		service := NewBaseImageService(config)

		// Add some mock images to cache
		service.Cache.Images = MockImageInfoList([]string{"test1.jpg", "test2.jpg"})
		service.Cache.UpdatedAt = time.Now()

		if len(service.Cache.Images) == 0 {
			t.Error("Cache should have images before clear")
		}

		service.ClearCache()

		if len(service.Cache.Images) != 0 {
			t.Errorf("Cache should be empty, got %d", len(service.Cache.Images))
		}
	})

	t.Run("should get cache status", func(t *testing.T) {
		config := models.ImageServiceConfig{
			UseLocal:    true,
			S3Bucket:    "test-bucket",
			EnableCache: true,
			CacheTTL:    10 * time.Minute,
		}

		service := NewBaseImageService(config)
		status := service.GetCacheStatus()

		expectedKeys := []string{"image_count", "updated_at", "ttl", "is_expired", "use_local", "s3_bucket"}

		for _, key := range expectedKeys {
			if _, ok := status[key]; !ok {
				t.Errorf("Missing key in status: %s", key)
			}
		}

		if status["use_local"] != true {
			t.Error("use_local should be true")
		}

		if status["s3_bucket"] != "test-bucket" {
			t.Errorf("s3_bucket mismatch: expected test-bucket, got %v", status["s3_bucket"])
		}
	})
}

// TestCacheExpiration tests cache expiration logic
func TestCacheExpiration(t *testing.T) {
	t.Run("should expire cache after TTL", func(t *testing.T) {
		config := models.ImageServiceConfig{
			EnableCache: true,
			CacheTTL:    1 * time.Millisecond,
		}

		service := NewBaseImageService(config)
		service.Cache.Images = MockImageInfoList([]string{"test1.jpg"})
		service.Cache.UpdatedAt = time.Now()

		// Wait for expiration
		time.Sleep(2 * time.Millisecond)

		if !service.Cache.IsExpired() {
			t.Error("Cache should be expired")
		}
	})

	t.Run("should not expire cache when TTL is 0", func(t *testing.T) {
		config := models.ImageServiceConfig{
			EnableCache: true,
			CacheTTL:    0,
		}

		service := NewBaseImageService(config)
		service.Cache.Images = MockImageInfoList([]string{"test1.jpg"})
		service.Cache.UpdatedAt = time.Now()

		if service.Cache.IsExpired() {
			t.Error("Cache should not expire when TTL is 0")
		}
	})
}
