package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"api/internal/models"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

func TestContactForm(t *testing.T) {
	// Set Gin to test mode
	gin.SetMode(gin.TestMode)

	t.Run("should return 400 when request body is invalid", func(t *testing.T) {
		router := gin.Default()
		router.POST("/api/contact", ContactForm)

		// Send invalid JSON
		req, _ := http.NewRequest("POST", "/api/contact", bytes.NewBufferString("invalid json"))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)

		var resp models.ContactResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.False(t, resp.Success)
		assert.Contains(t, resp.Message, "Invalid request format")
	})

	t.Run("should return 400 when required fields are missing", func(t *testing.T) {
		router := gin.Default()
		router.POST("/api/contact", ContactForm)

		// Missing name field
		reqBody := models.ContactRequest{
			Email:   "test@example.com",
			Subject: "Test Subject",
			Message: "Test message",
		}
		body, _ := json.Marshal(reqBody)

		req, _ := http.NewRequest("POST", "/api/contact", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)

		var resp models.ContactResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.False(t, resp.Success)
		assert.Contains(t, resp.Message, "required")
	})

	t.Run("should return 400 when email is missing", func(t *testing.T) {
		router := gin.Default()
		router.POST("/api/contact", ContactForm)

		reqBody := models.ContactRequest{
			Name:    "Test User",
			Subject: "Test Subject",
			Message: "Test message",
		}
		body, _ := json.Marshal(reqBody)

		req, _ := http.NewRequest("POST", "/api/contact", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)

		var resp models.ContactResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.False(t, resp.Success)
		assert.Contains(t, resp.Message, "required")
	})

	t.Run("should return 400 when subject is missing", func(t *testing.T) {
		router := gin.Default()
		router.POST("/api/contact", ContactForm)

		reqBody := models.ContactRequest{
			Name:    "Test User",
			Email:   "test@example.com",
			Message: "Test message",
		}
		body, _ := json.Marshal(reqBody)

		req, _ := http.NewRequest("POST", "/api/contact", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)

		var resp models.ContactResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.False(t, resp.Success)
		assert.Contains(t, resp.Message, "required")
	})

	t.Run("should return 400 when message is missing", func(t *testing.T) {
		router := gin.Default()
		router.POST("/api/contact", ContactForm)

		reqBody := models.ContactRequest{
			Name:    "Test User",
			Email:   "test@example.com",
			Subject: "Test Subject",
		}
		body, _ := json.Marshal(reqBody)

		req, _ := http.NewRequest("POST", "/api/contact", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusBadRequest, w.Code)

		var resp models.ContactResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.False(t, resp.Success)
		assert.Contains(t, resp.Message, "required")
	})

	t.Run("should succeed with valid data in dev mode", func(t *testing.T) {
		// Clear the environment variable for this test
		os.Setenv("CONTACT_API_URL", "")
		defer os.Setenv("CONTACT_API_URL", "")

		router := gin.Default()
		router.POST("/api/contact", ContactForm)

		reqBody := models.ContactRequest{
			Name:    "Test User",
			Email:   "test@example.com",
			Phone:   "+66 8X XXX XXXX",
			Subject: "Booking Inquiry",
			Message: "I would like to book a room for 3 nights.",
		}
		body, _ := json.Marshal(reqBody)

		req, _ := http.NewRequest("POST", "/api/contact", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.ContactResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp.Success)
		assert.Contains(t, resp.Message, "Thank you")
	})

	t.Run("should succeed with honeypot field filled (bot detection)", func(t *testing.T) {
		router := gin.Default()
		router.POST("/api/contact", ContactForm)

		// Honeypot field should trigger silent success
		reqBody := models.ContactRequest{
			Name:    "Bot",
			Email:   "bot@example.com",
			Subject: "Spam",
			Message: "Spam message",
			Website: "http://spam.com", // Honeypot field - should be ignored
		}
		body, _ := json.Marshal(reqBody)

		req, _ := http.NewRequest("POST", "/api/contact", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.ContactResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp.Success)
		assert.Contains(t, resp.Message, "Thank you")
	})
}

func TestSendToLambda(t *testing.T) {
	t.Run("should return nil in dev mode (no API URL)", func(t *testing.T) {
		os.Setenv("CONTACT_API_URL", "")
		defer os.Setenv("CONTACT_API_URL", "")

		req := models.ContactRequest{
			Name:    "Test User",
			Email:   "test@example.com",
			Phone:   "+66 8X XXX XXXX",
			Subject: "Test Subject",
			Message: "Test message",
		}

		err := sendToLambda(req, "")
		assert.NoError(t, err)
	})

	t.Run("should handle API URL when set (mock server)", func(t *testing.T) {
		// This test requires a mock server
		mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Verify the request method and headers
			assert.Equal(t, "POST", r.Method)
			assert.Equal(t, "application/json", r.Header.Get("Content-Type"))

			// Return success response
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{"success": true}`))
		}))
		defer mockServer.Close()

		os.Setenv("CONTACT_API_URL", mockServer.URL)
		defer os.Setenv("CONTACT_API_URL", "")

		req := models.ContactRequest{
			Name:    "Test User",
			Email:   "test@example.com",
			Phone:   "+66 8X XXX XXXX",
			Subject: "Test Subject",
			Message: "Test message",
		}

		err := sendToLambda(req, mockServer.URL)
		assert.NoError(t, err)
	})

	t.Run("should handle API errors gracefully", func(t *testing.T) {
		// Mock server that returns an error
		mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusInternalServerError)
			w.Write([]byte(`{"error": "Internal server error"}`))
		}))
		defer mockServer.Close()

		os.Setenv("CONTACT_API_URL", mockServer.URL)
		defer os.Setenv("CONTACT_API_URL", "")

		req := models.ContactRequest{
			Name:    "Test User",
			Email:   "test@example.com",
			Subject: "Test Subject",
			Message: "Test message",
		}

		err := sendToLambda(req, mockServer.URL)
		assert.Error(t, err)
		assert.Contains(t, err.Error(), "lambda returned status: 500")
	})
}

func TestContactFormIntegration(t *testing.T) {
	t.Run("full integration test with valid data", func(t *testing.T) {
		// Mock Lambda API
		mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
			w.Write([]byte(`{"success": true}`))
		}))
		defer mockServer.Close()

		os.Setenv("CONTACT_API_URL", mockServer.URL)
		defer os.Setenv("CONTACT_API_URL", "")

		router := gin.Default()
		router.POST("/api/contact", ContactForm)

		reqBody := models.ContactRequest{
			Name:    "Integration Test User",
			Email:   "integration@example.com",
			Phone:   "+66 8X XXX XXXX",
			Subject: "Room Booking",
			Message: "I would like to book the villa for 2 nights.",
		}
		body, _ := json.Marshal(reqBody)

		req, _ := http.NewRequest("POST", "/api/contact", bytes.NewBuffer(body))
		req.Header.Set("Content-Type", "application/json")
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var resp models.ContactResponse
		err := json.Unmarshal(w.Body.Bytes(), &resp)
		require.NoError(t, err)
		assert.True(t, resp.Success)
		assert.Contains(t, resp.Message, "Thank you")
	})
}
