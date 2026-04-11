import React from 'react';
import './ApprovalsPage.css';

function ApprovalsPage() {
  return (
    <div className="approvals-container">
      <div className="approvals-header">
        <h1>Approvals</h1>
        <p>Track and manage your document approvals</p>
      </div>

      <div className="approvals-empty">
        <div className="empty-icon">✓</div>
        <h2>No Approvals Found</h2>
        <p>You don't have any pending or recent approvals at the moment.</p>
        <p className="empty-subtitle">Applications you submit will appear here for approval tracking.</p>
      </div>

      <div className="approval-info-card">
        <h3>💡 How approvals work</h3>
        <ul>
          <li>Submit your application → Status shows as "Pending"</li>
          <li>Administrator reviews your documents → Status updates to "Under Review"</li>
          <li>Decision made → Status shows "Approved" or "Rejected"</li>
          <li>Check back here to track all approvals</li>
        </ul>
      </div>
    </div>
  );
}

export default ApprovalsPage;
