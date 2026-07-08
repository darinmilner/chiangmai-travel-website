package handlers

import (
	"log"
	"net/http"
	"time"

	"api/internal/loader"
	"api/internal/models"

	"github.com/gin-gonic/gin"
)

var HomepageData *models.HomePageData

func init() {
	var err error
	HomepageData, err = loader.LoadHomePageData()
	if err != nil {
		log.Printf("❌ Failed to load homepage data: %v", err)
		HomepageData = &models.HomePageData{
			Title:       "Chiang Mai Villa & Hostel",
			Description: "Your halal-friendly home in Chiang Mai",
			ActivePage:  "home",
		}
	}

	log.Printf("📊 FINAL: %d features, %d reasons, %d testimonials",
		len(HomepageData.Features),
		len(HomepageData.Reasons),
		len(HomepageData.Testimonials))
}

func HealthCheck(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":    "ok",
		"service":   "chiang-mai-business",
		"timestamp": time.Now().UTC().Format(time.RFC3339),
	})
}

func HomePage(c *gin.Context) {
	log.Println("🔵 HomePage handler called")
	// Make sure ActivePage is set to "home"
	HomepageData.ActivePage = "home"
	c.HTML(http.StatusOK, "index.html", HomepageData)
}

func GetHomepageData() *models.HomePageData {
	return HomepageData
}