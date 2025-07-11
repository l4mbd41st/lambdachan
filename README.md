![image](lambdachan.png)


# LambdaChan
LambdaChan is an imageboard engine meant to replace vichan, its based off TsukiChan.
## Development Notice
This project is currently in the very early stages of development and is not in a usable state. Please come back in the future.
## TODO
### High Priority
#### Architecture & Structure
- [ ] Move logic to modules:
  - [ ] `config.py` for `load_config()`
  - [ ] `database.py` for DB creation and queries
  - [ ] `routes.py` for all `@app.route` functions
  - [ ] `utils.py` for helpers like `is_allowed_filename`
- [ ] Use Flask Blueprints to separate routes (boards, threads, uploads)

#### Database & Models
- [ ] Add schema versioning or migration system (e.g., Alembic)
- [ ] Sanitize and validate `name`, `option`, `message` before DB insert
- [ ] Ensure foreign key constraints are enabled (`PRAGMA foreign_keys = ON;`)

#### Security
- [ ] Validate file extensions using MIME type, not filename
- [ ] Limit file size uploads
- [ ] Generate random filenames using UUID, not timestamp
- [ ] Sanitize user input to prevent XSS (autoescape in Jinja, bleach, etc.)
- [ ] Rate limit `/new` route to avoid spam (e.g., Flask-Limiter)

---

### Medium Priority
#### File Handling
- [ ] Clean up uploaded files after threads expire (e.g., keep last 100)
- [ ] Add a cron job or background task to remove old files
- [ ] Ensure uploads folder is not listable or index-accessible

#### Features & Logic
- [ ] Add CAPTCHA or challenge on post creation (e.g., hCaptcha)
- [ ] Add thread bumping when replies are added
- [ ] Display image previews instead of just links
- [ ] Add markdown or post formatting support

---

### Testing & Deployment
- [ ] Add unit tests for database operations and routes
- [ ] Use `.env` or environment variables instead of hardcoded config paths
- [ ] Add Dockerfile or deployment script
- [ ] Serve static files properly using nginx in production
- [ ] Turn off `debug=True` in production

---

### UI & UX
- [ ] Improve templates to display posts and replies clearly
- [ ] Add styling using CSS/JS (e.g., Bootstrap or custom CSS)
- [ ] Make board navigation consistent and accessible
- [ ] Add error messages and flash notifications for form validation
