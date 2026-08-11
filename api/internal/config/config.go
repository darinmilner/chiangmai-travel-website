package config

import (
	"os"
	"strconv"
	"time"

	"api/internal/models"
)

// LoadConfig loads configuration from environment variables
func LoadConfig() models.ImageServiceConfig {
	return models.ImageServiceConfig{
		S3Bucket:      getEnv("S3_BUCKET", ""),
		S3Region:      getEnv("AWS_REGION", "us-east-1"),
		S3Prefix:      getEnv("S3_PREFIX", "villa/"),
		CloudFrontURL: getEnv("CLOUDFRONT_URL", ""),
		LocalImageDir: getEnv("LOCAL_IMAGE_DIR", "static/images/villa"),
		UseLocal:      getBoolEnv("USE_LOCAL_IMAGES", false),
		CacheTTL:      getDurationEnv("IMAGE_CACHE_TTL", 5*time.Minute),
		EnableCache:   getBoolEnv("DISABLE_IMAGE_CACHE", true),
	}
}

// LoadFullConfig loads all application configuration
func LoadFullConfig() *AppConfig {
	return &AppConfig{
		Contact: ContactConfig{
			RecipientEmail: getEnv("CONTACT_RECIPIENT_EMAIL", ""),
			APIURL:         getEnv("CONTACT_API_URL", "https://your-api-gateway-url.com/contact"),
		},
		AWS: AWSConfig{
			Region:     getEnv("AWS_REGION", "us-east-1"),
			Bucket:     getEnv("S3_BUCKET", ""),
			CloudFront: getEnv("CLOUDFRONT_URL", ""),
		},
		Image: ImageConfig{
			LocalDir: getEnv("LOCAL_IMAGE_DIR", "static/images/villa"),
			UseLocal: getBoolEnv("USE_LOCAL_IMAGES", false),
		},
	}
}

// AppConfig holds all application configuration
type AppConfig struct {
	Contact ContactConfig
	AWS     AWSConfig
	Image   ImageConfig
}

// ContactConfig holds contact form configuration
type ContactConfig struct {
	RecipientEmail string
	APIURL         string
}

// AWSConfig holds AWS configuration
type AWSConfig struct {
	Region     string
	Bucket     string
	CloudFront string
}

// ImageConfig holds image configuration
type ImageConfig struct {
	LocalDir string
	UseLocal bool
}

// GetImageServiceConfig converts to models.ImageServiceConfig
func (c *AppConfig) GetImageServiceConfig() models.ImageServiceConfig {
	return models.ImageServiceConfig{
		S3Bucket:      c.AWS.Bucket,
		S3Region:      c.AWS.Region,
		CloudFrontURL: c.AWS.CloudFront,
		LocalImageDir: c.Image.LocalDir,
		UseLocal:      c.Image.UseLocal,
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func getBoolEnv(key string, defaultValue bool) bool {
	if value := os.Getenv(key); value != "" {
		if b, err := strconv.ParseBool(value); err == nil {
			return b
		}
	}
	return defaultValue
}

func getDurationEnv(key string, defaultValue time.Duration) time.Duration {
	if value := os.Getenv(key); value != "" {
		if d, err := time.ParseDuration(value); err == nil {
			return d
		}
	}
	return defaultValue
}
