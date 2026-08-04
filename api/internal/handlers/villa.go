package handlers

import (
	"context"
	"log"
	"net/http"
	"os"
	"time"

	"api/internal/models"
	"api/internal/services"
	"github.com/gin-gonic/gin"
)

var (
	imageService services.ImageService
	serviceInit  bool
)

// InitImageService initializes the image service
func InitImageService(config models.ImageServiceConfig) error {
	if serviceInit {
		return nil
	}

	factory := services.NewImageServiceFactory()

	// Get configuration from environment if not provided
	if config.S3Bucket == "" {
		config.S3Bucket = os.Getenv("S3_BUCKET")
	}
	if config.S3Region == "" {
		config.S3Region = os.Getenv("AWS_REGION")
	}
	if config.CloudFrontURL == "" {
		config.CloudFrontURL = os.Getenv("CLOUDFRONT_URL")
	}
	if config.LocalImageDir == "" {
		config.LocalImageDir = os.Getenv("LOCAL_IMAGE_DIR")
		if config.LocalImageDir == "" {
			config.LocalImageDir = "static/images/villa"
		}
	}

	// Check if we should use local
	useLocal := os.Getenv("USE_LOCAL_IMAGES") == "true" ||
		config.S3Bucket == "" ||
		os.Getenv("AWS_ACCESS_KEY_ID") == ""
	config.UseLocal = useLocal

	// Set cache TTL
	if config.CacheTTL == 0 {
		cacheTTL := os.Getenv("IMAGE_CACHE_TTL")
		if cacheTTL != "" {
			if ttl, err := time.ParseDuration(cacheTTL); err == nil {
				config.CacheTTL = ttl
			}
		}
		if config.CacheTTL == 0 {
			config.CacheTTL = 5 * time.Minute
		}
	}

	// Enable cache by default
	if os.Getenv("DISABLE_IMAGE_CACHE") != "true" {
		config.EnableCache = true
	}

	log.Printf("Initializing image service with config: useLocal=%v, bucket=%s, cacheTTL=%v",
		config.UseLocal, config.S3Bucket, config.CacheTTL)

	var err error
	imageService, err = factory.CreateService(config)
	if err != nil {
		return err
	}

	serviceInit = true
	return nil
}

// VillaPage handles the villa page rendering
func VillaPage(c *gin.Context) {
	if !serviceInit {
		log.Println("Image service not initialized, initializing with defaults")
		if err := InitImageService(models.ImageServiceConfig{}); err != nil {
			c.String(http.StatusInternalServerError, "Failed to initialize image service: %v", err)
			return
		}
	}

	ctx, cancel := context.WithTimeout(c.Request.Context(), 10*time.Second)
	defer cancel()

	data, err := imageService.GetVillaPageData(ctx, "The Villa", "villa")
	if err != nil {
		log.Printf("Error getting villa page data: %v", err)
		c.String(http.StatusInternalServerError, "Error loading images: %v", err)
		return
	}

	c.HTML(http.StatusOK, "villa", gin.H{
		"Title":      data.Title,
		"ActivePage": data.ActivePage,
		"Images":     data.Images,
		"ImagesJSON": data.ImagesJSON,
	})
}

// RefreshCacheHandler refreshes the image cache
func RefreshCacheHandler(c *gin.Context) {
	if !serviceInit {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Service not initialized"})
		return
	}

	imageService.ClearCache()
	c.JSON(http.StatusOK, gin.H{
		"message": "Cache cleared",
		"status":  imageService.GetCacheStatus(),
	})
}

// CacheStatusHandler returns cache status
func CacheStatusHandler(c *gin.Context) {
	if !serviceInit {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Service not initialized"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"status": imageService.GetCacheStatus(),
	})
}
