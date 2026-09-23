package handlers_test

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"api/internal/handlers"
	"api/internal/models"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestContactForm_Success(t *testing.T) {
	gin.SetMode(gin.TestMode)

	// 1. Mock API Gateway response
	mockAPIGateway := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		assert.Equal(t, "POST", r.Method)
		assert.Equal(t, "application/json", r.Header.Get("Content-Type"))

		var payload models.ContactRequest
		err := json.NewDecoder(r.Body).Decode(&payload)
		assert.NoError(t, err)
		assert.Equal(t, "Jane Doe", payload.Name)

		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"success": true}`))
	}))
	defer mockAPIGateway.Close()

	// 2. Override environment variable for mock API URL
	t.Setenv("CONTACT_API_URL", mockAPIGateway.URL)

	// 3. Set up Gin router
	router := gin.New()
	router.POST("/contact", handlers.ContactForm)

	reqPayload := models.ContactRequest{
		Name:    "Jane Doe",
		Email:   "jane@example.com",
		Subject: "Villa Inquiry",
		Message: "I want to inquire about rates.",
	}
	body, _ := json.Marshal(reqPayload)

	req := httptest.NewRequest("POST", "/contact", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	router.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp models.ContactResponse
	err := json.Unmarshal(rec.Body.Bytes(), &resp)
	assert.NoError(t, err)
	assert.True(t, resp.Success)
}

func TestContactForm_MissingFields(t *testing.T) {
	gin.SetMode(gin.TestMode)

	router := gin.New()
	router.POST("/contact", handlers.ContactForm)

	// Payload missing 'message'
	reqPayload := models.ContactRequest{
		Name:  "Jane Doe",
		Email: "jane@example.com",
	}
	body, _ := json.Marshal(reqPayload)

	req := httptest.NewRequest("POST", "/contact", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	router.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusBadRequest, rec.Code)
}
