package handlers

import (
	"html/template"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
)

func TestHomePage(t *testing.T) {
	// Set Gin to test mode
	gin.SetMode(gin.TestMode)

	t.Run("HomePage should return status 200", func(t *testing.T) {
		// Create a test router
		router := gin.Default()

		// Add the custom template functions BEFORE loading templates
		router.SetFuncMap(template.FuncMap{
			"add": func(a, b int) int { return a + b },
			"iterate": func(count int) []int {
				var result []int
				for i := 0; i < count; i++ {
					result = append(result, i)
				}
				return result
			},
		})

		// Load templates
		router.LoadHTMLGlob("../../templates/**/*.html")

		// Register the route
		router.GET("/", HomePage)

		// Create a test request
		req, err := http.NewRequest("GET", "/", nil)
		if err != nil {
			t.Fatalf("Failed to create request: %v", err)
		}

		// Record the response
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		// Check status code
		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}
		t.Logf("✅ Status code: %d", w.Code)
	})

	t.Run("HomePage should have non-nil data", func(t *testing.T) {
		// Ensure HomepageData is initialized
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
	})
}

// TestGetHomepageData tests the GetHomepageData function
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

// TestHomePageRendering tests the actual HTML rendering
func TestHomePageRendering(t *testing.T) {
	gin.SetMode(gin.TestMode)

	t.Run("HomePage should render HTML with data", func(t *testing.T) {
		router := gin.Default()

		// Add template functions
		router.SetFuncMap(template.FuncMap{
			"add": func(a, b int) int { return a + b },
			"iterate": func(count int) []int {
				var result []int
				for i := 0; i < count; i++ {
					result = append(result, i)
				}
				return result
			},
		})

		// Load templates - LoadHTMLGlob returns the engine, we don't need to capture it
		router.LoadHTMLGlob("../../templates/**/*.html")

		router.GET("/", HomePage)

		req, _ := http.NewRequest("GET", "/", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected status 200, got %d", w.Code)
		}

		// Check that HTML contains expected content
		body := w.Body.String()

		// Check for key content
		expectedStrings := []string{
			"VillaChiangMai",
			"Our Businesses",
			"Why Stay With Us?",
			"What Our Guests Say",
		}

		for _, expected := range expectedStrings {
			if !containsString(body, expected) {
				t.Errorf("Expected HTML to contain '%s', but it didn't", expected)
			} else {
				t.Logf("✅ HTML contains '%s'", expected)
			}
		}
	})
}

// Helper function to check if a string contains a substring
func containsString(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
