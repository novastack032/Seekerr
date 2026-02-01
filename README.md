# Lost&Found AI - Smart Item Recovery System

## 🎯 Hackathon Project Overview

**Lost&Found AI** is an intelligent item recovery platform that uses AI-powered matching to reunite people with their lost belongings. Built for a 24-hour hackathon, this system combines Natural Language Processing (NLP) with secure verification to solve the inefficiency of traditional lost-and-found systems.

## ✨ Key Features

### Core Functionality
- 🔍 **AI-Powered Matching**: TF-IDF + Cosine Similarity for intelligent item matching
- 📊 **Explainable Confidence Scores**: Transparent breakdown of match quality
- 🔒 **OTP Verification**: Fraud prevention through two-factor authentication
- 📈 **Analytics Dashboard**: Loss pattern insights and hotspot identification
- 🕐 **Recovery Timeline**: Complete tracking from report to recovery

### Innovation Highlights
- **Multi-factor Scoring**: Weighs description (60%), category (25%), and location (15%)
- **Real-time Matching**: Instant AI analysis on item submission
- **Secure Handover**: Both parties must verify identity via OTP
- **Pattern Analytics**: Identifies common loss locations and items

## 🛠 Tech Stack

- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Backend**: Python 3.x, Flask
- **Database**: SQLite
- **AI/ML**: scikit-learn (TfidfVectorizer, cosine_similarity)
- **Visualization**: Chart.js
- **Security**: OTP-based verification

## 📁 Project Structure

```
lostandfound-ai/
├── app.py                  # Main Flask application
├── database.py             # Database operations
├── matcher.py              # AI matching engine
├── otp_service.py          # OTP generation and verification
├── analytics.py            # Analytics calculations
├── requirements.txt        # Python dependencies
├── lostandfound.db         # SQLite database (auto-created)
├── static/
│   ├── css/
│   │   └── style.css       # Custom styles
│   ├── js/
│   │   └── main.js         # JavaScript functionality
│   └── uploads/            # User-uploaded images
└── templates/
    ├── index.html          # Landing page
    ├── report_lost.html    # Lost item form
    ├── report_found.html   # Found item form
    ├── matches.html        # Match results
    ├── verify.html         # OTP verification
    ├── timeline.html       # Recovery timeline
    ├── analytics.html      # Analytics dashboard
    └── my_items.html       # User dashboard
```

## 🚀 Quick Start Guide

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the project**
```bash
cd lostandfound-ai
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

4. **Access the application**
Open your browser and navigate to:
```
http://localhost:5000
```

## 📱 How to Use

### Reporting a Lost Item
1. Click "Report Lost Item" on the homepage
2. Fill in item details (category, description, location, etc.)
3. Submit the form
4. AI immediately searches for matching found items
5. Review top 3 matches with confidence scores

### Reporting a Found Item
1. Click "Report Found Item"
2. Provide item details
3. System matches against lost items database
4. Lost item owners are notified of potential matches

### Claiming an Item
1. Click "Claim This Item" on a match
2. System sends OTP to both claimer and finder
3. Both parties enter their OTPs to verify identity
4. Meet in a safe location for handover
5. Mark item as recovered

### Viewing Analytics
1. Navigate to Analytics Dashboard
2. View:
   - Most commonly lost items
   - Loss hotspots
   - Recovery success rate
   - Average recovery time

## 🤖 AI Matching Algorithm

### How It Works

1. **Text Preprocessing**
   - Combine category, item name, description, and color
   - Clean and normalize text (lowercase, remove special chars)

2. **Feature Extraction**
   - TF-IDF Vectorization with unigrams and bigrams
   - Converts text to numerical vectors

3. **Similarity Calculation**
   - Cosine similarity between lost and found items
   - Scores range from 0 (no match) to 1 (perfect match)

4. **Multi-Factor Scoring**
   ```
   Final Score = (Description × 0.60) + (Category × 0.25) + (Location × 0.15)
   ```

5. **Ranking & Filtering**
   - Returns top 3 matches above 40% threshold
   - Provides explainable breakdown for each score

### Example Match Explanation
```
85% Overall Match
├── Category: 100% (Exact match: "Phone")
├── Location: 70% (Same building)
└── Description: 82% (Similar keywords: black, iPhone, cracked screen)
```

## 🔐 Security Features

- **OTP Verification**: Prevents false claims
- **Two-Factor Handover**: Both parties must verify
- **Photo Upload**: Visual verification capability
- **Demo Mode**: Shows OTPs on screen for hackathon (production would use SMS)

## 📊 Database Schema

### Tables
- **lost_items**: Reported lost items
- **found_items**: Reported found items
- **matches**: AI-generated matches
- **verifications**: OTP verification records

## 🎨 Key Pages

1. **Landing Page** (`/`) - Hero section, stats, how it works
2. **Report Lost** (`/report_lost`) - Form to report lost items
3. **Report Found** (`/report_found`) - Form to report found items
4. **Matches** (`/matches`) - AI match results with explainability
5. **Verify** (`/verify`) - OTP verification portal
6. **Timeline** (`/timeline`) - Recovery journey tracking
7. **Analytics** (`/analytics`) - Loss pattern insights
8. **My Items** (`/my_items`) - User dashboard

## 🎯 Judging Points to Highlight

### Technical Innovation
- ✅ Real AI/ML implementation (not just keywords)
- ✅ Explainable AI with confidence breakdowns
- ✅ Multi-factor scoring algorithm

### Problem Solving
- ✅ Addresses real-world inefficiency
- ✅ Fraud prevention through OTP
- ✅ Transparency via timeline tracking

### User Experience
- ✅ Clean, intuitive interface
- ✅ Mobile-responsive design
- ✅ Visual feedback and explanations

### Scalability
- ✅ Modular architecture
- ✅ Database-driven approach
- ✅ Easy to extend with new features

## 🚀 Future Enhancements

### Short-term (1-3 months)
- Image recognition using CNNs
- Mobile app (React Native)
- SMS notifications via Twilio
- Multi-language support

### Medium-term (3-6 months)
- Geofencing and GPS alerts
- In-app chat between users
- QR code tagging system
- Blockchain handover records

### Long-term (6+ months)
- Enterprise API for institutions
- Predictive loss analytics
- AR visualization
- Global network integration

## 🐛 Troubleshooting

### Common Issues

**Database not found**
```bash
# The database is auto-created on first run
# If issues persist, delete lostandfound.db and restart
```

**Import errors**
```bash
# Ensure all dependencies are installed
pip install -r requirements.txt
```

**Port already in use**
```bash
# Change port in app.py
app.run(debug=True, host='0.0.0.0', port=5001)
```

## 📝 Demo Script for Judges

1. **Show Landing Page** - Explain problem statement
2. **Report Lost Item** - Demo form submission
3. **Show AI Matches** - Highlight confidence scores and explainability
4. **Claim Item** - Demonstrate OTP verification
5. **View Timeline** - Show recovery journey
6. **Analytics Dashboard** - Display insights and charts
7. **Explain Algorithm** - Walk through TF-IDF + cosine similarity

## 🏆 Competitive Advantages

- **Actual AI** (not just keyword matching)
- **Explainable confidence scores**
- **Security-first approach**
- **Data-driven insights**
- **Complete end-to-end solution**

## 👥 Team & Credits

- **Project Type**: Hackathon Submission
- **Duration**: 24 hours
- **Stack**: Full-stack web application
- **AI Model**: Custom NLP pipeline

## 📄 License

MIT License - Free for educational and hackathon purposes

## 🙏 Acknowledgments

- Bootstrap for UI framework
- Chart.js for visualizations
- scikit-learn for NLP capabilities
- Flask community for excellent documentation

---

**Built with ❤️ for the Hackathon**

*Reuniting People with Their Belongings, One AI Match at a Time*