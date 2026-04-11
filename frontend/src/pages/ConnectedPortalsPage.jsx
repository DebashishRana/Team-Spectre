import React, { useState } from 'react';
import './ConnectedPortalsPage.css';

function ConnectedPortalsPage() {
  const [activatedServices, setActivatedServices] = useState({});

  const handleActivate = (serviceId) => {
    setActivatedServices(prev => ({
      ...prev,
      [serviceId]: !prev[serviceId]
    }));
  };

  const services = [
    {
      id: 'digilocker',
      name: 'Digilocker',
      icon: '📁',
      description: 'Access your digital documents and certificates securely. Import and store all your important documents in one place.',
      features: ['Digital Vault', 'E-Sign Documents', 'Share Securely'],
      status: 'Integration Ready',
      integration_url: 'https://digilocker.gov.in'
    },
    {
      id: 'umang',
      name: 'UMANG App',
      icon: '📱',
      description: 'Unified Mobile Application for New-age Governance. Access multiple government services through one mobile application.',
      features: ['All Services', 'Real-time Updates', 'Easy Access'],
      status: 'Integration Ready',
      integration_url: 'https://www.umang.gov.in'
    },
    {
      id: 'aadhaar',
      name: 'Aadhaar Services',
      icon: '🆔',
      description: 'Use your Aadhaar for identity verification. Seamlessly integrate Aadhaar authentication for quick onboarding.',
      features: ['eKYC', '12-digit Verification', 'Quick Auth'],
      status: 'Integration Ready',
      integration_url: 'https://www.uidai.gov.in'
    }
  ];

  const schemes = [
    {
      id: 'scheme1',
      name: 'Digital India',
      category: 'Technology',
      description: 'Bridging the digital divide across the nation',
      icon: '🌐',
      link: '#'
    },
    {
      id: 'scheme2',
      name: 'Jan Dhan Yojana',
      category: 'Finance',
      description: 'Financial inclusion for all citizens',
      icon: '💰',
      link: '#'
    },
    {
      id: 'scheme3',
      name: 'Skill India',
      category: 'Education',
      description: 'Empowering youth with professional skills',
      icon: '🎓',
      link: '#'
    },
    {
      id: 'scheme4',
      name: 'Ayushman Bharat',
      category: 'Health',
      description: 'Universal health coverage for all citizens',
      icon: '🏥',
      link: '#'
    },
    {
      id: 'scheme5',
      name: 'Pradhan Mantri Awas',
      category: 'Housing',
      description: 'Housing for all - affordable housing scheme',
      icon: '🏠',
      link: '#'
    },
    {
      id: 'scheme6',
      name: 'Make in India',
      category: 'Business',
      description: 'Encouraging manufacturing and innovation',
      icon: '🏭',
      link: '#'
    }
  ];

  return (
    <div className="connected-portals-container">
      {/* Header */}
      <div className="portals-header">
        <h1>Connected Portals</h1>
        <p>Integrate with government services and access schemes</p>
      </div>

      {/* Services Section */}
      <section className="services-section">
        <div className="section-header">
          <h2>Integrated Services</h2>
          <p>Connect with major government platforms for seamless experience</p>
        </div>

        <div className="services-grid">
          {services.map((service) => (
            <div key={service.id} className="service-card">
              <div className="service-header">
                <span className="service-icon">{service.icon}</span>
                <h3>{service.name}</h3>
              </div>

              <p className="service-description">{service.description}</p>

              <div className="service-features">
                {service.features.map((feature, idx) => (
                  <span key={idx} className="feature-badge">{feature}</span>
                ))}
              </div>

              <div className="service-status">
                <span className="status-badge">{service.status}</span>
              </div>

              <button
                className={`activate-btn ${activatedServices[service.id] ? 'activated' : ''}`}
                onClick={() => handleActivate(service.id)}
              >
                {activatedServices[service.id] ? '✓ Activated' : 'Activate'}
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Schemes Section */}
      <section className="schemes-section">
        <div className="section-header">
          <h2>Government Schemes & Services</h2>
          <p>Explore and apply for various government schemes available through this portal</p>
        </div>

        <div className="schemes-grid">
          {schemes.map((scheme) => (
            <div key={scheme.id} className="scheme-card">
              <div className="scheme-icon">{scheme.icon}</div>
              <h3 className="scheme-name">{scheme.name}</h3>
              <span className="scheme-category">{scheme.category}</span>
              <p className="scheme-description">{scheme.description}</p>
              <a href={scheme.link} className="scheme-link">
                Learn More →
              </a>
            </div>
          ))}
        </div>
      </section>

      {/* Connection Info */}
      <section className="connection-info">
        <div className="info-card">
          <h3>🔐 Secure Connection</h3>
          <p>All services are connected through secure, encrypted channels. Your data is protected with industry-standard encryption.</p>
        </div>
        <div className="info-card">
          <h3>📋 Data Privacy</h3>
          <p>We respect your privacy. Services are only accessed with your explicit permission and data is never shared without consent.</p>
        </div>
        <div className="info-card">
          <h3>⚙️ One-Click Integration</h3>
          <p>Activate services with a single click. Instantly sync your documents and access government schemes seamlessly.</p>
        </div>
      </section>
    </div>
  );
}

export default ConnectedPortalsPage;
