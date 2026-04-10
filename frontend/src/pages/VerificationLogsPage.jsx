import React, { useState, useEffect } from 'react';
import './VerificationLogsPage.css';

const VerificationLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    documentType: '',
    status: '',
    searchTerm: ''
  });
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 10,
    total: 0
  });
  const [selectedLog, setSelectedLog] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  // Fetch extraction logs
  useEffect(() => {
    fetchLogs();
  }, [filters, pagination.skip]);

  const fetchLogs = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const userId = localStorage.getItem('user_id') || 1; // Get from auth
      
      let url = `http://localhost:8000/api/user-extraction-logs/${userId}?skip=${pagination.skip}&limit=${pagination.limit}`;
      
      if (filters.documentType) {
        url += `&document_type=${filters.documentType}`;
      }
      if (filters.status) {
        url += `&status=${filters.status}`;
      }
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch logs');
      
      const data = await response.json();
      
      // Apply search filter on client side
      let filtered = data.records || [];
      if (filters.searchTerm) {
        filtered = filtered.filter(log => {
          const term = filters.searchTerm.toLowerCase();
          return (
            log.document_type.toLowerCase().includes(term) ||
            log.extracted_data?.id_number?.includes(filters.searchTerm) ||
            log.extracted_data?.full_name?.toLowerCase().includes(term)
          );
        });
      }
      
      setLogs(filtered);
      setPagination(prev => ({
        ...prev,
        total: data.total_count
      }));
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Failed to load extraction logs');
      setLogs([]);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'valid':
        return 'verified';
      case 'partial':
        return 'review';
      case 'invalid':
        return 'flagged';
      default:
        return 'unknown';
    }
  };

  const getStatusBadgeClass = (status) => {
    const color = getStatusColor(status);
    return `badge badge-${color}`;
  };

  const getConfidenceColor = (confidenceStr) => {
    const confidence = parseInt(confidenceStr || '0');
    if (confidence >= 85) return 'high-confidence';
    if (confidence >= 70) return 'medium-confidence';
    return 'low-confidence';
  };

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    setPagination(prev => ({ ...prev, skip: 0 })); // Reset pagination on filter change
  };

  const handleViewDetails = (log) => {
    setSelectedLog(log);
    setShowDetails(true);
  };

  const handleCloseDetails = () => {
    setShowDetails(false);
    setTimeout(() => setSelectedLog(null), 300);
  };

  const handleExportCSV = () => {
    if (logs.length === 0) {
      alert('No records to export');
      return;
    }

    const headers = ['Document ID', 'Document Type', 'Confidence Score', 'Status', 'Date', 'Extracted ID', 'Name'];
    const rows = logs.map(log => [
      log.id,
      log.document_type,
      log.confidence_score,
      log.validation_status,
      new Date(log.created_at).toLocaleDateString(),
      log.extracted_data?.id_number || '-',
      log.extracted_data?.full_name || '-'
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `extraction-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleNextPage = () => {
    if ((pagination.skip + pagination.limit) < pagination.total) {
      setPagination(prev => ({
        ...prev,
        skip: prev.skip + prev.limit
      }));
    }
  };

  const handlePreviousPage = () => {
    if (pagination.skip > 0) {
      setPagination(prev => ({
        ...prev,
        skip: Math.max(0, prev.skip - prev.limit)
      }));
    }
  };

  return (
    <div className="verification-logs-container">
      <div className="logs-header">
        <h1 className="page-title">Verification History</h1>
        <p className="page-subtitle">Track all your document extractions and verifications</p>
      </div>

      {/* Filters Section */}
      <div className="filters-section">
        <div className="filter-group">
          <label htmlFor="searchTerm">Search</label>
          <input
            type="text"
            id="searchTerm"
            name="searchTerm"
            placeholder="Search by name, ID, or document type..."
            value={filters.searchTerm}
            onChange={handleFilterChange}
            className="search-input"
          />
        </div>

        <div className="filter-group">
          <label htmlFor="documentType">Document Type</label>
          <select
            id="documentType"
            name="documentType"
            value={filters.documentType}
            onChange={handleFilterChange}
            className="filter-select"
          >
            <option value="">All Types</option>
            <option value="aadhaar">Aadhaar</option>
            <option value="pan">PAN</option>
            <option value="passport">Passport</option>
            <option value="driving_license">Driving License</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="status">Status</label>
          <select
            id="status"
            name="status"
            value={filters.status}
            onChange={handleFilterChange}
            className="filter-select"
          >
            <option value="">All Status</option>
            <option value="valid">Valid</option>
            <option value="partial">Partial</option>
            <option value="invalid">Invalid</option>
          </select>
        </div>

        <div className="filter-actions">
          <button onClick={handleExportCSV} className="btn btn-export">
            📥 Export to CSV
          </button>
        </div>
      </div>

      {/* Loading & Error States */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Loading extraction history...</p>
        </div>
      )}

      {error && (
        <div className="error-state">
          <p className="error-message">⚠️ {error}</p>
          <button onClick={fetchLogs} className="btn btn-retry">Retry</button>
        </div>
      )}

      {!loading && !error && logs.length === 0 && (
        <div className="empty-state">
          <p className="empty-icon">📋</p>
          <p className="empty-message">No verification records found</p>
          <p className="empty-subtext">Upload and verify documents to see them here</p>
        </div>
      )}

      {/* Logs Table */}
      {!loading && !error && logs.length > 0 && (
        <div className="logs-table-container">
          <table className="logs-table">
            <thead>
              <tr>
                <th>Document ID</th>
                <th>Document Type</th>
                <th>Confidence Score</th>
                <th>Status</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id} className="log-row">
                  <td className="id-cell">#{log.id}</td>
                  <td className="doc-type">
                    <span className="doc-type-badge">
                      {log.document_type.toUpperCase()}
                    </span>
                  </td>
                  <td>
                    <div className="confidence-container">
                      <span className={`confidence-score ${getConfidenceColor(log.confidence_score)}`}>
                        {log.confidence_score}
                      </span>
                      <div className="confidence-bar">
                        <div 
                          className={`confidence-fill ${getConfidenceColor(log.confidence_score)}`}
                          style={{ width: `${parseInt(log.confidence_score) || 0}%` }}
                        ></div>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span className={getStatusBadgeClass(log.validation_status)}>
                      {log.validation_status.charAt(0).toUpperCase() + log.validation_status.slice(1)}
                    </span>
                  </td>
                  <td className="date-cell">
                    {new Date(log.created_at).toLocaleDateString('en-IN', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </td>
                  <td>
                    <button 
                      onClick={() => handleViewDetails(log)}
                      className="btn btn-view-details"
                      title="View extracted data"
                    >
                      👁️ View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Pagination */}
      {!loading && !error && logs.length > 0 && (
        <div className="pagination-container">
          <div className="pagination-info">
            Showing {Math.min(pagination.skip + 1, pagination.total)}-{Math.min(pagination.skip + pagination.limit, pagination.total)} of {pagination.total}
          </div>
          <div className="pagination-buttons">
            <button 
              onClick={handlePreviousPage} 
              disabled={pagination.skip === 0}
              className="btn btn-pagination"
            >
              ← Previous
            </button>
            <button 
              onClick={handleNextPage}
              disabled={(pagination.skip + pagination.limit) >= pagination.total}
              className="btn btn-pagination"
            >
              Next →
            </button>
          </div>
        </div>
      )}

      {/* Details Modal */}
      {showDetails && selectedLog && (
        <div className={`modal-overlay ${showDetails ? 'active' : ''}`} onClick={handleCloseDetails}>
          <div className="modal-content" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Extraction Details</h2>
              <button className="modal-close" onClick={handleCloseDetails}>&times;</button>
            </div>
            
            <div className="modal-body">
              <div className="detail-section">
                <h3>Document Information</h3>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Document ID</label>
                    <span>#{selectedLog.id}</span>
                  </div>
                  <div className="detail-item">
                    <label>Document Type</label>
                    <span className="doc-type-badge">{selectedLog.document_type.toUpperCase()}</span>
                  </div>
                  <div className="detail-item">
                    <label>Confidence Score</label>
                    <span className={getConfidenceColor(selectedLog.confidence_score)}>
                      {selectedLog.confidence_score}
                    </span>
                  </div>
                  <div className="detail-item">
                    <label>Validation Status</label>
                    <span className={`badge badge-${getStatusColor(selectedLog.validation_status)}`}>
                      {selectedLog.validation_status.toUpperCase()}
                    </span>
                  </div>
                  <div className="detail-item">
                    <label>Extraction Date</label>
                    <span>
                      {new Date(selectedLog.created_at).toLocaleDateString('en-IN', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                        hour: '2-digit',
                        minute: '2-digit',
                        second: '2-digit'
                      })}
                    </span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h3>Extracted Information</h3>
                <div className="detail-grid">
                  {selectedLog.extracted_data?.full_name && (
                    <div className="detail-item">
                      <label>Full Name</label>
                      <span>{selectedLog.extracted_data.full_name}</span>
                    </div>
                  )}
                  {selectedLog.extracted_data?.id_number && (
                    <div className="detail-item">
                      <label>{selectedLog.document_type.toUpperCase()} Number</label>
                      <span className="masked-text">{selectedLog.extracted_data.id_number}</span>
                    </div>
                  )}
                  {selectedLog.extracted_data?.date_of_birth && (
                    <div className="detail-item">
                      <label>Date of Birth</label>
                      <span>{selectedLog.extracted_data.date_of_birth}</span>
                    </div>
                  )}
                  {selectedLog.extracted_data?.gender && (
                    <div className="detail-item">
                      <label>Gender</label>
                      <span>{selectedLog.extracted_data.gender}</span>
                    </div>
                  )}
                  {selectedLog.extracted_data?.phone && (
                    <div className="detail-item">
                      <label>Phone</label>
                      <span className="masked-text">{selectedLog.extracted_data.phone}</span>
                    </div>
                  )}
                  {selectedLog.extracted_data?.address && (
                    <div className="detail-item">
                      <label>Address</label>
                      <span>{selectedLog.extracted_data.address}</span>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button onClick={handleCloseDetails} className="btn btn-close">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VerificationLogsPage;
