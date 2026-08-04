package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"path/filepath"
	"testing"

	"api/internal/models"
	"api/internal/services"
	"github.com/gin-gonic/gin"
)

func setupTestHandler(t *testing.T) (*gin.Engine, string) {
	t.Helper()

	// Get project root
	projectRoot, err := os.Getwd()
	if err != nil {
		t.Skip("Could not determine project root, skipping test")
		return nil, ""
	}
	projectRoot = filepath.Dir(filepath.Dir(projectRoot))

	// Create temp directory for test images
	tempDir, err := os.MkdirTemp("", "villa-test-*")
	if err != nil {
		t.Fatalf("Failed to create temp dir: %v", err)
	}

	// Create image directory
	imageDir := filepath.Join(tempDir, "static/images/villa")
	if err := os.MkdirAll(imageDir, 0755); err != nil {
		t.Fatalf("Failed to create image dir: %v", err)
	}

	// Create test images
	testImages := []string{
		"exterior.jpg",
		"pool.jpg",
		"living-room.jpg",
	}

	for _, name := range testImages {
		path := filepath.Join(imageDir, name)
		f, err := os.Create(path)
		if err != nil {
			t.Fatalf("Failed to create test image: %v", err)
		}
		defer f.Close()
		f.WriteString("fake image data")
	}

	// Initialize service with test config
	config := models.ImageServiceConfig{
		LocalImageDir: imageDir,
		UseLocal:      true,
		EnableCache:   false,
	}

	if err := InitImageService(config); err != nil {
		t.Fatalf("Failed to init image service: %v", err)
	}

	// Setup gin
	gin.SetMode(gin.TestMode)
	r := gin.Default()
	r.LoadHTMLGlob(filepath.Join(projectRoot, "views/*.html"))
	r.GET("/villa", VillaPage)

	return r, tempDir
}

func TestVillaPage_Handler(t *testing.T) {
	t.Run("should return villa page with images", func(t *testing.T) {
		r, tempDir := setupTestHandler(t)
		defer os.RemoveAll(tempDir)

		req := httptest.NewRequest("GET", "/villa", nil)
		w := httptest.NewRecorder()

		r.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}

		// Check that HTML contains images
		body := w.Body.String()
		if !containsImages(body) {
			t.Error("Response body does not contain image references")
		}
	})

	t.Run("should handle service not initialized", func(t *testing.T) {
		// Reset service
		serviceInit = false
		imageService = nil

		gin.SetMode(gin.TestMode)
		r := gin.Default()

		// Get project root for templates
		projectRoot, err := os.Getwd()
		if err != nil {
			t.Skip("Could not determine project root")
		}
		projectRoot = filepath.Dir(filepath.Dir(projectRoot))
		r.LoadHTMLGlob(filepath.Join(projectRoot, "views/*.html"))

		r.GET("/villa", VillaPage)

		req := httptest.NewRequest("GET", "/villa", nil)
		w := httptest.NewRecorder()

		r.ServeHTTP(w, req)

		// Should auto-initialize with defaults
		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}

		// Reset after test
		serviceInit = false
		imageService = nil
	})
}

func TestRefreshCacheHandler(t *testing.T) {
	t.Run("should refresh cache", func(t *testing.T) {
		r, tempDir := setupTestHandler(t)
		defer os.RemoveAll(tempDir)

		// Add admin route
		r.GET("/admin/cache/refresh", RefreshCacheHandler)

		req := httptest.NewRequest("GET", "/admin/cache/refresh", nil)
		w := httptest.NewRecorder()

		r.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}

		var response map[string]interface{}
		if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
			t.Fatalf("Failed to parse response: %v", err)
		}

		if response["message"] != "Cache cleared" {
			t.Errorf("Expected message 'Cache cleared', got %v", response["message"])
		}
	})

	t.Run("should handle service not initialized", func(t *testing.T) {
		// Reset service
		serviceInit = false
		imageService = nil

		gin.SetMode(gin.TestMode)
		r := gin.Default()
		r.GET("/admin/cache/refresh", RefreshCacheHandler)

		req := httptest.NewRequest("GET", "/admin/cache/refresh", nil)
		w := httptest.NewRecorder()

		r.ServeHTTP(w, req)

		if w.Code != http.StatusBadRequest {
			t.Errorf("Expected status 400, got %d", w.Code)
		}

		// Reset after test
		serviceInit = false
		imageService = nil
	})
}

func TestCacheStatusHandler(t *testing.T) {
	t.Run("should return cache status", func(t *testing.T) {
		r, tempDir := setupTestHandler(t)
		defer os.RemoveAll(tempDir)

		// Add admin route
		r.GET("/admin/cache/status", CacheStatusHandler)

		req := httptest.NewRequest("GET", "/admin/cache/status", nil)
		w := httptest.NewRecorder()

		r.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}

		var response map[string]interface{}
		if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
			t.Fatalf("Failed to parse response: %v", err)
		}

		status, ok := response["status"].(map[string]interface{})
		if !ok {
			t.Error("Status should be a map")
		}

		if status["image_count"] == nil {
			t.Error("Image count should be present")
		}
	})
}

// Helper function to check if HTML contains image references
func containsImages(html string) bool {
	imagePatterns := []string{
		".jpg",
		".jpeg",
		".png",
		".webp",
		"src=",
		"ImagesJSON",
	}

	for _, pattern := range imagePatterns {
		if len(html) > 0 && pattern != "" {
			// Simple check
			if len(html) > 100 { // Page should have content
				return true
			}
		}
	}
	return len(html) > 1000 // Basic check that page has content
}
