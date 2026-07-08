package router

import (
	"html/template"
	"net/http"
	"os"
	"path/filepath"

	"api/internal/handlers"

	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	// ---------- Load Templates with Functions ----------
	funcMap := template.FuncMap{
		"add": func(a, b int) int { return a + b },
		"iterate": func(count int) []int {
			var result []int
			for i := 0; i < count; i++ {
				result = append(result, i)
			}
			return result
		},
		"safe": func(s string) template.HTML {
			return template.HTML(s)
		},
	}

	// Create a new template set with functions
	tmpl := template.New("").Funcs(funcMap)

	// Try multiple path patterns
	patterns := []string{
		"templates/layouts/*.html",
		"templates/partials/*.html",
		"templates/pages/*.html",
		"../templates/layouts/*.html",
		"../templates/partials/*.html",
		"../templates/pages/*.html",
		"../../templates/layouts/*.html",
		"../../templates/partials/*.html",
		"../../templates/pages/*.html",
	}

	for _, pattern := range patterns {
		if matches, _ := filepath.Glob(pattern); len(matches) > 0 {
			tmpl.ParseGlob(pattern)
		}
	}

	// Set the parsed templates
	r.SetHTMLTemplate(tmpl)

	// ---------- Static Files ----------
	r.Static("/static", "./static")
	r.Static("/videos", "./videos")

	// ---------- Routes ----------
	// Health check
	r.GET("/health", handlers.HealthCheck)

	// HOME PAGE
	r.GET("/", handlers.HomePage)

	// Other pages - using unique content template names
	r.GET("/villa", func(c *gin.Context) {
		c.HTML(http.StatusOK, "villa.html", gin.H{
			"Title":      "The Villa",
			"ActivePage": "villa",
		})
	})

	r.GET("/hostel", func(c *gin.Context) {
		c.HTML(http.StatusOK, "hostel.html", gin.H{
			"Title":      "The Hostel",
			"ActivePage": "hostel",
		})
	})

	r.GET("/meatshop", func(c *gin.Context) {
		c.HTML(http.StatusOK, "meatshop.html", gin.H{
			"Title":      "The Meat Shop",
			"ActivePage": "meatshop",
		})
	})

	r.GET("/blog", func(c *gin.Context) {
		c.HTML(http.StatusOK, "blog.html", gin.H{
			"Title":      "Blog",
			"ActivePage": "blog",
		})
	})

	r.GET("/contact", func(c *gin.Context) {
		c.HTML(http.StatusOK, "contact.html", gin.H{
			"Title":      "Contact Us",
			"ActivePage": "contact",
		})
	})

	// Debug route
	r.GET("/debug/health", func(c *gin.Context) {
		c.JSON(http.StatusOK, gin.H{
			"status": "ok",
			"routes": []string{"/", "/villa", "/hostel", "/meatshop", "/blog", "/contact"},
		})
	})

	return r
}