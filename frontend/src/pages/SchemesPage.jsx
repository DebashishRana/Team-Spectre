import React, { useState } from 'react';
import './SchemesPage.css';

const SchemesPage = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [activeTab, setActiveTab] = useState('categories');
  const [selectedCategory, setSelectedCategory] = useState(null);

  const schemes = [
    { id: 1, name: 'Post Office Monthly Income Scheme', ministry: 'Ministry Of Finance', icon: '📈', color: '#FF9500' },
    { id: 2, name: 'Pradhan Mantri Awas Yojana - Urban', ministry: 'Ministry Of Housing & Urban Affairs', icon: '📈', color: '#FF9500' },
    { id: 3, name: 'Pradhan Mantri Jeevan Jyoti Bima Yojana', ministry: 'Ministry Of Finance', icon: '📈', color: '#FF9500' }
  ];

  const categories = [
    { id: 1, name: 'Agriculture, Rural & Environment', count: 838, icon: '🚜', bgColor: '#E8F5E9' },
    { id: 2, name: 'Banking, Financial Services and Insurance', count: 324, icon: '🏦', bgColor: '#F3E5F5' },
    { id: 3, name: 'Business & Entrepreneurship', count: 736, icon: '₹', bgColor: '#FFF3E0' },
    { id: 4, name: 'Education & Learning', count: 1088, icon: '🎓', bgColor: '#FCE4EC' },
    { id: 5, name: 'Health & Wellness', count: 287, icon: '✚', bgColor: '#E0F2F1' },
    { id: 6, name: 'Housing & Shelter', count: 133, icon: '🏢', bgColor: '#E3F2FD' },
    { id: 7, name: 'Public Safety, Law & Justice', count: 33, icon: '⚖️', bgColor: '#F1F8E9' },
    { id: 8, name: 'Science, IT & Communications', count: 108, icon: '🧬', bgColor: '#FFF9C4' },
    { id: 9, name: 'Skills & Employment', count: 391, icon: '💼', bgColor: '#FFEBEE' },
    { id: 10, name: 'Social welfare & Empowerment', count: 1450, icon: '👥', bgColor: '#F3E5F5' },
    { id: 11, name: 'Sports & Culture', count: 259, icon: '🎭', bgColor: '#E8EAF6' },
    { id: 12, name: 'Transport & Infrastructure', count: 99, icon: '🚗', bgColor: '#E0F2F1' },
    { id: 13, name: 'Travel & Tourism', count: 97, icon: '✈️', bgColor: '#FFF8E1' },
    { id: 14, name: 'Utility & Sanitation', count: 58, icon: '🔧', bgColor: '#F5F5F5' },
    { id: 15, name: 'Women and Child', count: 464, icon: '👩', bgColor: '#FCE4EC' }
  ];

  const states = ['Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh', 'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka', 'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu', 'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal'];

  const centrMinistries = [
    'Ministry of Finance',
    'Ministry of Housing & Urban Affairs',
    'Ministry of Agriculture & Farmers Welfare',
    'Ministry of Health & Family Welfare',
    'Ministry of Education',
    'Ministry of Labour & Employment',
    'Ministry of Social Justice & Empowerment',
    'Ministry of Women & Child Development'
  ];

  const filteredCategories = categories.filter(cat =>
    cat.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="schemes-page-wrapper">
      {/* Hero Section */}
      <div className="schemes-hero">
        <h1 className="schemes-title">Schemes on Seva Setu portal</h1>
        <p className="schemes-subtitle">
          Explore seamless access to many government services and schemes at one place, ensuring hassle-free and transparent experience for citizens.
        </p>

        {/* Search Bar */}
        <div className="search-bar-container">
          <input
            type="text"
            placeholder="Search For Schemes"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="schemes-search-input"
          />
          <button className="search-btn">🔍</button>
        </div>

        {/* Explore Eligible Schemes */}
        <button className="explore-eligible-btn">
          <span className="explore-icon">⭐</span>
          Explore Eligible Schemes
          <span className="explore-arrow">›</span>
        </button>
      </div>

      {/* Trending Schemes */}
      <div className="trending-section">
        <div className="trending-header">
          <h2>Trending Schemes</h2>
          <a href="#" className="view-all-link">View All (8)</a>
        </div>

        <div className="trending-carousel">
          {schemes.map(scheme => (
            <div key={scheme.id} className="trending-card">
              <div className="trending-icon" style={{ backgroundColor: scheme.color }}>
                {scheme.icon}
              </div>
              <div className="trending-content">
                <h3>{scheme.name}</h3>
                <p>{scheme.ministry}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Explore Schemes Section */}
      <div className="explore-schemes-section">
        <div className="explore-header">
          <h2>Explore schemes</h2>
          <a href="#" className="view-all-link">View All</a>
        </div>

        {/* Tabs */}
        <div className="tabs-container">
          <button
            className={`tab-btn ${activeTab === 'categories' ? 'active' : ''}`}
            onClick={() => setActiveTab('categories')}
          >
            Categories
          </button>
          <button
            className={`tab-btn ${activeTab === 'states' ? 'active' : ''}`}
            onClick={() => setActiveTab('states')}
          >
            State/UTs
          </button>
          <button
            className={`tab-btn ${activeTab === 'ministries' ? 'active' : ''}`}
            onClick={() => setActiveTab('ministries')}
          >
            Central Ministries
          </button>
        </div>

        {/* Categories Grid */}
        {activeTab === 'categories' && (
          <div className="categories-grid">
            {filteredCategories.map(category => (
              <div
                key={category.id}
                className="category-card"
                style={{ backgroundColor: category.bgColor }}
                onClick={() => setSelectedCategory(category)}
              >
                <div className="category-icon">{category.icon}</div>
                <div className="category-content">
                  <h3 className="category-name">{category.name}</h3>
                  <p className="category-count">
                    <span className="count-number">{category.count}</span>
                    <span className="count-label">Schemes</span>
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* States Grid */}
        {activeTab === 'states' && (
          <div className="states-grid">
            {states.map((state, idx) => (
              <div key={idx} className="state-card">
                <span className="state-code">
                  {state.substring(0, 2).toUpperCase()}
                </span>
                <h4>{state}</h4>
              </div>
            ))}
          </div>
        )}

        {/* Central Ministries Grid */}
        {activeTab === 'ministries' && (
          <div className="ministries-grid">
            {centrMinistries.map((ministry, idx) => (
              <div key={idx} className="ministry-card">
                <span className="ministry-icon">🏛️</span>
                <h4>{ministry}</h4>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Category Detail Modal */}
      {selectedCategory && (
        <div className="modal-overlay" onClick={() => setSelectedCategory(null)}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedCategory(null)}>✕</button>
            <div className="modal-icon" style={{ backgroundColor: selectedCategory.bgColor }}>
              {selectedCategory.icon}
            </div>
            <h2>{selectedCategory.name}</h2>
            <p className="modal-count">{selectedCategory.count} Schemes Available</p>
            <button className="modal-btn-explore">Explore Schemes</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SchemesPage;
