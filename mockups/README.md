# Cardora UI Mockups

Production-ready, interactive HTML mockups for the Cardora credit card management application.

## 📁 Files Created

### 1. **design-system.html**
Complete design system showcase featuring:
- Color palette (Primary Blue, Secondary Purple, Category colors)
- Typography scale
- Button variants (Primary, Secondary, Outline, Danger, Success, Disabled)
- Form inputs (Text, Password, Select, Error states)
- Cards (Basic, Stat cards, Credit card design)
- Badges and alerts
- Progress bars
- Data tables

**Open this first** to understand the visual language and components used throughout the app.

### 2. **login.html**
Modern authentication page with:
- Split-screen layout (form left, features right)
- Email and password fields with icons
- Remember me checkbox
- Forgot password link
- Social login buttons (Google, GitHub)
- Sign up link
- Animated gradient background on feature section
- Fully responsive design

**Features highlighted**: AI extraction, smart categorization, analytics

### 3. **dashboard.html**
Main application dashboard featuring:
- **Top navigation** with search bar and user profile
- **Sidebar navigation** with menu items
- **4 stat cards** (Total spending, Transactions, Active cards, AI accuracy)
- **2 charts** powered by Chart.js:
  - Line chart for spending trends
  - Doughnut chart for category breakdown
- **Recent transactions table** with category badges
- **Credit card preview** with utilization progress bar
- Real-time data visualization

**This is the heart of the application** - shows what users see after login.

### 4. **upload.html**
PDF statement upload page with:
- **Drag & drop zone** with file validation
- **Upload progress simulation** with multiple stages:
  - Uploading file (30%)
  - Extracting text from PDF (60%)
  - AI processing transactions (85%)
  - Complete (100%)
- **Success result display** showing:
  - Extraction summary (66 transactions, $2,087, 93% AI confidence, 8 categories)
  - Auto-created credit card with full details
  - Category distribution with progress bars
  - Call-to-action buttons
- **Feature highlights** section (AI-powered, Fast, Secure)

**This demonstrates your core feature** - the AI-powered PDF extraction.

---

## 🎨 Design Features

### Visual Quality
✅ Modern, sleek UI inspired by Linear, Vercel, Stripe
✅ Consistent color scheme throughout
✅ Smooth hover effects and transitions
✅ Professional gradients and shadows
✅ Responsive layouts (mobile, tablet, desktop)

### Interactions
✅ Working drag & drop for file upload
✅ Animated progress bars
✅ Interactive charts (Chart.js)
✅ Hover states on all interactive elements
✅ Loading state simulations

### Technologies Used
- **Tailwind CSS** via CDN (same as you'll use in Next.js)
- **Chart.js** for dashboard visualizations
- **Vanilla JavaScript** for interactions
- **Google Fonts** (Inter font family)

---

## 🚀 How to Use

### View the Mockups

1. **Open any HTML file in your browser**:
   ```
   # Windows
   E:\Cardora\mockups\design-system.html
   E:\Cardora\mockups\login.html
   E:\Cardora\mockups\dashboard.html
   E:\Cardora\mockups\upload.html
   ```

2. **Recommended viewing order**:
   1. `design-system.html` - Understand the components
   2. `login.html` - See the entry point
   3. `dashboard.html` - Experience the main interface
   4. `upload.html` - Test the core feature

### Test Interactions

**login.html**:
- Fill out the form and click "Sign in" to see loading state
- Click "Sign up for free" or social login buttons

**dashboard.html**:
- Charts are fully rendered with Chart.js
- Hover over table rows for highlight effect
- Click "View All" links (placeholders)

**upload.html**:
- Drag and drop a PDF file (or any file to test validation)
- Click the upload area to browse files
- Watch the multi-stage upload simulation
- See the complete success result with all extracted data

---

## 🎯 Next Steps

### Option 1: Iterate on Design
If you want to change colors, spacing, or layouts:
1. Open the HTML file in a code editor
2. Modify Tailwind classes or CSS
3. Refresh browser to see changes
4. Repeat until satisfied

### Option 2: Convert to Next.js
Once you approve these designs, I can:
1. Create a new Next.js 14+ project (App Router)
2. Set up shadcn/ui components
3. Convert these HTML mockups to React components
4. Wire up your backend APIs
5. Add authentication and routing

---

## 📊 Design Specifications

### Colors
- **Primary (Blue)**: `#0ea5e9` (Sky-500)
- **Secondary (Purple)**: `#a855f7` (Purple-500)
- **Categories**:
  - Groceries: `#4CAF50` (Green)
  - Dining: `#FF6B6B` (Red)
  - Transport: `#2196F3` (Blue)
  - Shopping: `#FF9800` (Orange)
  - Bills & Utilities: `#9C27B0` (Purple)
  - Entertainment: `#00BCD4` (Cyan)
  - Healthcare: `#E91E63` (Pink)
  - Others: `#9E9E9E` (Gray)

### Typography
- **Font Family**: Inter (Google Fonts)
- **Sizes**:
  - H1: 2.25rem (36px) - Bold
  - H2: 1.875rem (30px) - Bold
  - H3: 1.5rem (24px) - Semibold
  - Body: 1rem (16px) - Regular
  - Small: 0.875rem (14px) - Regular

### Spacing
- **Component Padding**: 1.5rem (24px)
- **Card Padding**: 1.5rem (24px)
- **Section Spacing**: 2rem (32px)
- **Grid Gap**: 1.5rem (24px)

### Shadows
- **Small**: `shadow-sm`
- **Medium**: `shadow-md`
- **Large**: `shadow-lg`

---

## ✨ Key Features Showcased

1. **Modern Authentication** (login.html)
   - Clean, professional design
   - Feature highlights for new users
   - Social login options

2. **Rich Dashboard** (dashboard.html)
   - Real-time data visualization
   - Multiple chart types
   - Quick stats overview
   - Recent activity feed

3. **Smart Upload** (upload.html)
   - Intuitive drag & drop
   - Visual progress feedback
   - Detailed success summary
   - Auto-created card display

4. **Consistent Design** (design-system.html)
   - Reusable components
   - Standardized colors
   - Predictable interactions

---

## 💡 Design Decisions

### Why Tailwind CSS?
- Same framework you'll use in Next.js
- Easy to convert to production components
- Rapid prototyping
- Consistent design tokens

### Why These Pages?
- **Login**: First user touchpoint
- **Dashboard**: Most frequently used page
- **Upload**: Core value proposition
- **Design System**: Foundation for all other pages

### Why No Navigation Between Pages?
- Each is a standalone mockup for review
- Easier to share with stakeholders
- When converting to Next.js, we'll add proper routing

---

## 📝 Feedback Checklist

Review each mockup and consider:
- [ ] Do the colors match your brand vision?
- [ ] Is the spacing comfortable to read?
- [ ] Are the components visually consistent?
- [ ] Do the interactions feel smooth?
- [ ] Is the information hierarchy clear?
- [ ] Does the upload flow make sense?
- [ ] Are the charts readable and informative?
- [ ] Does the design feel modern and professional?

---

## 🔄 Making Changes

If you want to modify anything:

**Change Colors**:
```html
<!-- In tailwind.config -->
primary: {
    500: '#YOUR_COLOR_HERE',
}
```

**Adjust Spacing**:
```html
<!-- Change from p-6 to p-8 for more padding -->
<div class="p-8">...</div>
```

**Modify Fonts**:
```html
<!-- Change font-semibold to font-bold -->
<h3 class="font-bold">...</h3>
```

Then refresh the browser to see changes immediately!

---

## ⏭️ What's Next?

Once you're happy with these mockups, we can:
1. Create additional pages (Transactions, Analytics, Cards, Profile)
2. Convert everything to Next.js 14+ with App Router
3. Integrate with your FastAPI backend
4. Add authentication flows
5. Deploy to production

**Estimated time to convert to Next.js**: 2-3 hours
**Estimated time for full production app**: 6-8 hours

---

## 📞 Ready to Proceed?

Let me know if you want to:
- **Iterate**: Change colors, spacing, or layouts
- **Expand**: Create more page mockups
- **Build**: Convert to Next.js and start development

These mockups are your blueprint for a production-ready application! 🚀
