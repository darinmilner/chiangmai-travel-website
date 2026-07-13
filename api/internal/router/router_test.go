package router

import (
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestSetupRouterReturnsEngine(t *testing.T) {
	r := SetupRouter()

	assert.NotNil(t, r)
	assert.IsType(t, &gin.Engine{}, r)
}

func TestSetupRouterReleaseMode(t *testing.T) {
	original := os.Getenv("GIN_MODE")
	defer os.Setenv("GIN_MODE", original)

	os.Setenv("GIN_MODE", "release")

	SetupRouter()

	assert.Equal(t, gin.ReleaseMode, gin.Mode())
}

func TestHealthEndpointExists(t *testing.T) {
	r := SetupRouter()

	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	w := httptest.NewRecorder()

	r.ServeHTTP(w, req)

	// Assumes handlers.HealthCheck returns 200.
	assert.Equal(t, http.StatusOK, w.Code)
}

func TestRoutesRegistered(t *testing.T) {
	r := SetupRouter()

	routes := r.Routes()

	expected := map[string]string{
		"GET /health":   "",
		"GET /":         "",
		"GET /villa":    "",
		"GET /hostel":   "",
		"GET /meatshop": "",
		"GET /blog":     "",
		"GET /contact":  "",
	}

	for _, route := range routes {
		delete(expected, route.Method+" "+route.Path)
	}

	assert.Empty(t, expected)
}
