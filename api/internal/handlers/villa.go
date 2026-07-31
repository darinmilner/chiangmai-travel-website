package handlers

import (
	"encoding/json"
	"net/http"
	"os"
	"path/filepath"
	"strings"

	"github.com/gin-gonic/gin"
	"html/template"
)

func VillaPage(c *gin.Context) {
	imageDir := "static/images/villa"
	var images []string

	files, err := os.ReadDir(imageDir)
	if err == nil {
		for _, file := range files {
			if !file.IsDir() {
				name := file.Name()
				ext := strings.ToLower(filepath.Ext(name))
				if ext == ".jpg" || ext == ".jpeg" || ext == ".png" || ext == ".webp" || ext == ".gif" {
					images = append(images, "/static/images/villa/"+name)
				}
			}
		}
	}

	if len(images) == 0 {
		images = []string{
			"/static/images/villa/exterior.jpg",
			"/static/images/villa/pool.jpg",
			"/static/images/villa/living-room.jpg",
			"/static/images/villa/kitchen.jpg",
			"/static/images/villa/bedroom.jpg",
			"/static/images/villa/garden.jpg",
		}
	}

	imagesJSON, err := json.Marshal(images)
	if err != nil {
		c.String(http.StatusInternalServerError, err.Error())
		return
	}

	c.HTML(http.StatusOK, "villa", gin.H{
		"Title":      "The Villa",
		"ActivePage": "villa",
		"Images":     images,
		"ImagesJSON": template.JS(imagesJSON),
	})
}
