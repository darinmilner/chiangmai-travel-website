package handlers

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestHomePage(t *testing.T) {
	// Set Gin to test mode
	gin.SetMode(gin.TestMode)

	t.Run("HomePage should have non-nil data", func(t *testing.T) {
		if HomepageData == nil {
			t.Error("❌ HomepageData is nil")
			return
		}
		t.Logf("✅ HomepageData is not nil")
	})

	t.Run("HomePage data should have features", func(t *testing.T) {
		if HomepageData == nil {
			t.Skip("HomepageData is nil, skipping test")
			return
		}

		if len(HomepageData.Features) == 0 {
			t.Errorf("❌ Expected at least 1 feature, got %d", len(HomepageData.Features))
		} else {
			t.Logf("✅ Found %d features", len(HomepageData.Features))
			// Log first feature for debugging
			t.Logf("   First feature: %+v", HomepageData.Features[0])
		}
	})

	t.Run("HomePage data should have reasons", func(t *testing.T) {
		if HomepageData == nil {
			t.Skip("HomepageData is nil, skipping test")
			return
		}

		if len(HomepageData.Reasons) == 0 {
			t.Errorf("❌ Expected at least 1 reason, got %d", len(HomepageData.Reasons))
		} else {
			t.Logf("✅ Found %d reasons", len(HomepageData.Reasons))
		}
	})

	t.Run("HomePage data should have testimonials", func(t *testing.T) {
		if HomepageData == nil {
			t.Skip("HomepageData is nil, skipping test")
			return
		}

		if len(HomepageData.Testimonials) == 0 {
			t.Errorf("❌ Expected at least 1 testimonial, got %d", len(HomepageData.Testimonials))
		} else {
			t.Logf("✅ Found %d testimonials", len(HomepageData.Testimonials))
		}
	})

	t.Run("HomePage data should have Hero Headline", func(t *testing.T) {
		if HomepageData == nil {
			t.Skip("HomepageData is nil, skipping test")
			return
		}

		if HomepageData.Hero.Headline == "" {
			t.Errorf("❌ Hero Headline is empty")
		} else {
			t.Logf("✅ Hero Headline: '%s'", HomepageData.Hero.Headline)
		}
	})

	t.Run("HomePage data should have CTA Title", func(t *testing.T) {
		if HomepageData == nil {
			t.Skip("HomepageData is nil, skipping test")
			return
		}

		if HomepageData.CTA.Title == "" {
			t.Errorf("❌ CTA Title is empty")
		} else {
			t.Logf("✅ CTA Title: '%s'", HomepageData.CTA.Title)
		}
	})
}

func TestHealthCheck(t *testing.T) {
	gin.SetMode(gin.TestMode)

	t.Run("HealthCheck should return 200", func(t *testing.T) {
		router := gin.Default()
		router.GET("/health", HealthCheck)

		req, _ := http.NewRequest("GET", "/health", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}
		t.Logf("✅ HealthCheck status: %d", w.Code)
	})

	t.Run("HealthCheck should return JSON", func(t *testing.T) {
		router := gin.Default()
		router.GET("/health", HealthCheck)

		req, _ := http.NewRequest("GET", "/health", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		contentType := w.Header().Get("Content-Type")
		if contentType != "application/json; charset=utf-8" {
			t.Errorf("Expected JSON content type, got %s", contentType)
		}
		t.Logf("✅ Content-Type: %s", contentType)

		// Verify response is valid JSON
		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		if err != nil {
			t.Errorf("❌ Response is not valid JSON: %v", err)
		} else {
			t.Logf("✅ Response is valid JSON: %+v", response)
		}
	})
}

func TestGetHomepageData(t *testing.T) {
	t.Run("GetHomepageData should return non-nil data", func(t *testing.T) {
		data := GetHomepageData()
		if data == nil {
			t.Error("❌ GetHomepageData returned nil")
		} else {
			t.Logf("✅ GetHomepageData returned data with %d features", len(data.Features))
		}
	})
}

func TestHomepageDataJSON(t *testing.T) {
	t.Run("HomepageData should be JSON serializable", func(t *testing.T) {
		if HomepageData == nil {
			t.Skip("HomepageData is nil, skipping test")
			return
		}

		// Try to marshal to JSON
		jsonData, err := json.Marshal(HomepageData)
		if err != nil {
			t.Errorf("❌ Failed to marshal HomepageData to JSON: %v", err)
		} else {
			t.Logf("✅ HomepageData is JSON serializable (%d bytes)", len(jsonData))
		}
	})
}
