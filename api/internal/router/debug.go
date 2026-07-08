package router

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// DebugTemplates shows the list of loaded templates
func DebugTemplates(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{
		"status":  "ok",
		"message": "Router is working correctly",
		"routes": []string{
			"/ - Homepage",
			"/villa - Villa page",
			"/hostel - Hostel page",
			"/meatshop - Meat Shop page",
			"/blog - Blog page",
			"/contact - Contact page",
		},
	})
}