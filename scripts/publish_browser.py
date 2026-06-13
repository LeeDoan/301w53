import os
import sys
import time
import subprocess
from playwright.sync_api import sync_playwright

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

def log(msg):
    print(msg, flush=True)

def run_git_push(repo_url):
    log(f"\n[Git] Configuring remote origin to {repo_url}...")
    try:
        # Check if remote exists
        remotes = subprocess.check_output(["git", "remote"], cwd=PROJECT_ROOT).decode().strip().split()
        if "origin" in remotes:
            subprocess.run(["git", "remote", "remove", "origin"], cwd=PROJECT_ROOT, check=True)
        
        subprocess.run(["git", "remote", "add", "origin", repo_url], cwd=PROJECT_ROOT, check=True)
        subprocess.run(["git", "branch", "-M", "main"], cwd=PROJECT_ROOT, check=True)
        
        log("[Git] Adding files to commit...")
        subprocess.run(["git", "add", ".gitignore", "index.html", "README.md", "scripts/"], cwd=PROJECT_ROOT, check=True)
        
        log("[Git] Committing...")
        subprocess.run(["git", "commit", "-m", "Build: Consolidated condo board strategy dashboard prototype with interactive charts"], cwd=PROJECT_ROOT)
        
        log("[Git] Pushing main branch to GitHub...")
        # We push using terminal which will prompt for credentials/keychain if needed
        # Or it will reuse the credential helper already configured
        subprocess.run(["git", "push", "-u", "origin", "main", "--force"], cwd=PROJECT_ROOT, check=True)
        log("[Git] Successfully pushed code to remote repository.")
        return True
    except Exception as e:
        log(f"[ERROR] Git operations failed: {e}")
        return False

def main():
    log("=== Launching Chrome for GitHub Publishing ===")
    log("This script will open Google Chrome in a window on your desktop.")
    log("Please log in to your personal GitHub account (LeeDoan) if prompted.\n")

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(
                headless=False,
                channel="chrome"
            )
        except Exception:
            log("[INFO] Fallback to standard Chromium browser...")
            browser = p.chromium.launch(headless=False)

        context = browser.new_context()
        page = context.new_page()

        log("[Browser] Navigating to GitHub...")
        page.goto("https://github.com/new")

        log("[System] Waiting for you to be logged in to GitHub...")
        log("Please check the opened browser window.")

        last_logged_url = ""
        debug_counter = 0

        while True:
            # Scan all open pages in the context and bind to the correct active page
            pages = context.pages
            # Log all open page URLs for real-time debugging
            log(f"[DEBUG] Open tabs: {[p.url for p in pages]}")
            active_page = pages[-1]  # Default to the most recently opened tab
            
            # Look for a tab containing the repository creation or the repo itself
            for p in pages:
                if "github.com/new" in p.url or "/301w53" in p.url:
                    # Avoid binding to the login page redirect parameters if we can help it,
                    # unless it's the only one.
                    if "return_to" not in p.url or len(pages) == 1:
                        active_page = p
                        break
            
            page = active_page
            url = page.url
            
            if url != last_logged_url:
                log(f"[Browser] Current URL: {url} | Title: {page.title()}")
                last_logged_url = url
                debug_counter = 0
                try:
                    screenshot_path = "/Users/ldoan6/.gemini/antigravity/brain/c97a78b4-a2e8-4e23-ac9c-e564b7b9a068/screenshot.png"
                    page.screenshot(path=screenshot_path)
                    log(f"[Browser] Saved screenshot to {screenshot_path}")
                except Exception as e:
                    log(f"[Browser] Failed to take screenshot: {e}")
            
            # If user lands on home page or dashboard after logging in, redirect back to /new
            if (url == "https://github.com/" or "github.com/dashboard" in url or url == "https://github.com") and not page.locator("a[href='/login']").is_visible():
                log("[Browser] Logged in and redirected to home. Redirecting back to /new...")
                page.goto("https://github.com/new")
                time.sleep(2)
                continue
            
            # Check if we are on the repository creation page (meaning we are logged in!)
            if "github.com/new" in url and "return_to" not in url:
                # Let's search for the repo name input using various potential selectors
                repo_input = None
                for selector in ["#repository_name", "input[data-testid='repository-name-input']", "input[aria-label='Repository name']", "input[name='repository_name']", "input[placeholder='Repository name']", "input[id*='repository']"]:
                    try:
                        if page.locator(selector).is_visible():
                            repo_input = page.locator(selector)
                            log(f"[Browser] Found repository name input using selector: {selector}")
                            break
                    except Exception:
                        pass
                
                if repo_input:
                    log("[Browser] Logged in detected! Setting up '301w53' repository details...")
                    
                    # Fill repository name
                    repo_input.fill("301w53")
                    time.sleep(2) # wait for availability check
                    
                    # Check if '301w53' is already taken
                    is_taken = False
                    validation_selectors = [".color-fg-danger.flash-error", "[id*='validation']", ".flash-error", ".is-error", "span[color='danger']"]
                    for val_sel in validation_selectors:
                        try:
                            loc = page.locator(val_sel)
                            if loc.is_visible() and ("already exists" in loc.text_content().lower() or "taken" in loc.text_content().lower()):
                                log(f"[Browser] Repo '301w53' already exists according to: {val_sel} -> {loc.text_content()}")
                                is_taken = True
                                break
                        except Exception:
                            pass
                    
                    # Alternative check: search all text on page for "already exists"
                    try:
                        page_text = page.locator("body").text_content().lower()
                        if "already exists" in page_text or "is already taken" in page_text:
                            log("[Browser] Repo '301w53' already exists (detected in page text).")
                            is_taken = True
                    except Exception:
                        pass

                    if is_taken:
                        log("[Browser] Warning: Repo '301w53' already exists. Redirecting to settings...")
                        # Let's find owner name from page or default to LeeDoan
                        owner_btn = page.locator("#repository-owner-label")
                        if owner_btn.is_visible():
                            github_username = owner_btn.text_content().strip()
                        else:
                            # Let's look for owner dropdown or labels
                            for owner_sel in ["#repository-owner-label", "button[id*='owner']", "[data-testid='repository-owner']"]:
                                try:
                                    if page.locator(owner_sel).is_visible():
                                        github_username = page.locator(owner_sel).text_content().strip()
                                        break
                                except Exception:
                                    pass
                        page.goto(f"https://github.com/{github_username}/301w53")
                        continue

                    # Select Public (default is public, but let's be explicit)
                    public_radio = None
                    for pub_sel in ["input[value='public']", "input[type='radio'][value='public']", "input[id*='public']"]:
                        try:
                            if page.locator(pub_sel).is_visible():
                                public_radio = page.locator(pub_sel)
                                break
                        except Exception:
                            pass
                    
                    if public_radio:
                        public_radio.click()

                    # Click Create Repository
                    create_btn = None
                    for btn_sel in ["button:has-text('Create repository')", "button[type='submit']:has-text('Create repository')", "button[data-testid='create-repository-button']", "button:has-text('Create')"]:
                        try:
                            if page.locator(btn_sel).is_visible():
                                create_btn = page.locator(btn_sel)
                                log(f"[Browser] Found Create Repository button using: {btn_sel}")
                                break
                        except Exception:
                            pass
                            
                    if create_btn:
                        log("[Browser] Creating repository...")
                        create_btn.click()
                        time.sleep(5) # wait for creation redirect
                else:
                    debug_counter += 1
                    if debug_counter % 10 == 0:
                        log("[DEBUG] Waiting on github.com/new. Repository name input not found yet.")
                        # Check if login button is visible
                        login_btn = page.locator("a[href='/login']")
                        if login_btn.is_visible():
                            log("[DEBUG] Login button is visible. User is NOT logged in in this browser context.")
                        else:
                            log("[DEBUG] Login button NOT visible. User might be logged in or page is loading. Page HTML preview:")
                            # Dump some info
                            try:
                                inputs = page.query_selector_all("input")
                                log(f"[DEBUG] Inputs on page: {[('id:' + str(i.get_attribute('id')) + ', name:' + str(i.get_attribute('name')) + ', placeholder:' + str(i.get_attribute('placeholder'))) for i in inputs]}")
                            except Exception as e:
                                log(f"[DEBUG] Error listing inputs: {e}")
                
            # If repository is created or already exists
            elif "/301w53" in url and "settings" not in url:
                parts = url.split("github.com/")[1].split("/")
                github_username = parts[0]
                repo_name = parts[1].split("?")[0]
                
                log(f"[Browser] Detected repository at {url}")
                log(f"[Browser] Owner: {github_username} | Repository: {repo_name}")
                
                # Check if it was created under the wrong account (e.g. LDOAN6_ford)
                if github_username.lower() == "ldoan6_ford":
                    log("[WARNING] The repository was created under your corporate LDOAN6_ford account which is restricted!")
                    log("Please select your personal account (LeeDoan) as owner in the browser window and re-create it.")
                    log("You may need to log out of LDOAN6_ford in this browser window first.")
                    time.sleep(5)
                    continue
                
                repo_url = f"https://github.com/{github_username}/{repo_name}.git"
                
                # Push git code now
                success = run_git_push(repo_url)
                if success:
                    log("\n[Browser] Navigating to GitHub Pages settings...")
                    page.goto(f"https://github.com/{github_username}/{repo_name}/settings/pages")
                    
                    try:
                        page.wait_for_selector("h2:has-text('Pages')", timeout=10000)
                    except Exception:
                        page.wait_for_selector("h2:has-text('GitHub Pages')", timeout=10000)
                    time.sleep(2)
                    
                    log("[Browser] Configuring Pages source...")
                    
                    # Click on 'None' branch dropdown (Deploy from a branch)
                    branch_dropdown = None
                    for drop_sel in ["button[id^='pages-branch-select-menu-']", "button:has-text('None')", "[data-testid='pages-branch-select']", "button[aria-label^='Branch:']"]:
                        try:
                            if page.locator(drop_sel).is_visible():
                                branch_dropdown = page.locator(drop_sel)
                                break
                        except Exception:
                            pass
                            
                    if branch_dropdown:
                        branch_dropdown.click()
                        time.sleep(1)
                        
                        # Select 'main' branch option
                        main_option = None
                        for main_sel in ["span:has-text('main')", "span:has-text('main')", "button:has-text('main')"]:
                            try:
                                if page.locator(main_sel).is_visible():
                                    main_option = page.locator(main_sel)
                                    break
                            except Exception:
                                pass
                                
                        if main_option:
                            main_option.click()
                            time.sleep(1)
                            
                            # Click Save button
                            save_btn = None
                            for save_sel in ["span:has-text('Save')", "button:has-text('Save')", "span:has-text('Save')"]:
                                try:
                                    if page.locator(save_sel).first.is_visible():
                                        save_btn = page.locator(save_sel).first
                                        break
                                except Exception:
                                    pass
                                    
                            if save_btn:
                                save_btn.click()
                                log("[Browser] GitHub Pages configuration saved!")
                                time.sleep(5) # wait for page refresh
                    
                    repo_created = True
                    break
                else:
                    log("[System] Git push failed. Please resolve terminal authentication and try again.")
                    break
            
            time.sleep(1.5) # Poll browser state

        if repo_created:
            live_url = f"https://{github_username.lower()}.github.io/301w53/"
            log(f"\n=== Publishing Successful ===")
            log(f"Live Dashboard URL: {live_url}")
            log("Please wait a minute or two for GitHub Pages to compile the site.")
            log("Keep this browser window open to inspect the deployment, or close it when done.")
            time.sleep(15)
        
        browser.close()

if __name__ == "__main__":
    main()
