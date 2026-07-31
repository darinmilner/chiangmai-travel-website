package router

import (
	"html/template"
	"net/http"
	"os"

	"api/internal/handlers"
	"github.com/gin-gonic/gin"
)

func SetupRouter() *gin.Engine {
	if os.Getenv("GIN_MODE") == "release" {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.Default()

	funcMap := template.FuncMap{
		"add": func(a, b int) int {
			return a + b
		},
		"iterate": func(count int) []int {
			result := make([]int, count)
			for i := 0; i < count; i++ {
				result[i] = i
			}
			return result
		},
		"safe": func(s string) template.HTML {
			return template.HTML(s)
		},
	}

	r.HTMLRender = createRenderer(funcMap)

	r.Static("/static", "./static")
	r.Static("/videos", "./videos")

	r.GET("/health", handlers.HealthCheck)

	r.GET("/", func(c *gin.Context) {
		data := handlers.GetHomepageData()
		if data == nil {
			c.String(http.StatusInternalServerError, "Data not loaded")
			return
		}

		data.Title = "Chiang Mai Travel"
		data.ActivePage = "home"

		c.HTML(http.StatusOK, "index", data)
	})

	r.GET("/villa", handlers.VillaPage)

	r.GET("/hostel", func(c *gin.Context) {
		c.HTML(http.StatusOK, "hostel", gin.H{
			"Title":      "Hostel",
			"ActivePage": "hostel",
		})
	})

	r.GET("/meatshop", func(c *gin.Context) {
		c.HTML(http.StatusOK, "meatshop", gin.H{
			"Title":      "Meat Shop",
			"ActivePage": "meatshop",
		})
	})

	r.GET("/blog", func(c *gin.Context) {
		c.HTML(http.StatusOK, "blog", gin.H{
			"Title":      "Blog",
			"ActivePage": "blog",
		})
	})

	r.GET("/contact", func(c *gin.Context) {
		c.HTML(http.StatusOK, "contact", gin.H{
			"Title":      "Contact",
			"ActivePage": "contact",
		})
	})

	r.POST("/api/contact", handlers.ContactForm)

	return r
}
