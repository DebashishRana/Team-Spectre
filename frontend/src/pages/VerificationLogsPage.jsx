import React, { useState, useEffect } from 'react';
import './VerificationLogsPage.css';

const VerificationLogsPage = () => {
  const [logs, setLogs] = useState([
    {
      id: 39635,
      document_type: 'aadhaar',
      confidence_score: '94.6%',
      validation_status: 'valid',
      created_at: '2024-01-15T10:30:00',
      extracted_data: {
        full_name: 'Kristin Watson',
        id_number: '3818 8009 2292',
        date_of_birth: '11/10/1987',
        gender: 'Female',
        phone: '+91 98765 43210',
        address: 'Orange, California'
      }
    },
    {
      id: 22739,
      document_type: 'pan',
      confidence_score: '87.3%',
      validation_status: 'partial',
      created_at: '2024-01-10T14:45:00',
      extracted_data: {
        full_name: 'Theresa Webb',
        id_number: 'ABCDE1234F',
        date_of_birth: '02/15/1992',
        gender: 'Female',
        phone: '+91 87654 32109',
        address: 'Fairfield, New York'
      }
    }
  ]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('latest');
  const [pagination, setPagination] = useState({
    skip: 0,
    limit: 10,
    total: 0,
    currentPage: 1
  });
  const [selectedLog, setSelectedLog] = useState(null);
  const [showDetails, setShowDetails] = useState(false);

  // Fetch extraction logs
  useEffect(() => {
    fetchLogs();
  }, [sortBy, pagination.skip]);

  const fetchLogs = async () => {
    setLoading(false); // Use mock data immediately for visualization
    // For demo: comment out actual API call to use mock data
    // Uncomment the section below when ready to test with real data
    
    /*
    setLoading(true);
    setError(null);
    
    try {
      const userId = localStorage.getItem('user_id') || 1;
      let url = `http://localhost:8000/api/user-extraction-logs/${userId}?skip=${pagination.skip}&limit=${pagination.limit}`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error('Failed to fetch logs');
      
      const data = await response.json();
      let records = data.records || [];
      
      // Apply sorting
      if (sortBy === 'latest') {
        records.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } else if (sortBy === 'oldest') {
        records.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
      }
      
      setLogs(records);
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
    */
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'valid':
        return '#27ae60'; // Green
      case 'partial':
        return '#f39c12'; // Amber
      case 'invalid':
        return '#e74c3c'; // Red
      default:
        return '#95a5a6'; // Gray
    }
  };

  const handleViewDetails = (log, e) => {
    if (e) e.stopPropagation();
    setSelectedLog(log);
    setShowDetails(true);
  };

  const handleCloseDetails = () => {
    setShowDetails(false);
    setTimeout(() => setSelectedLog(null), 300);
  };

  const handleDownloadCSV = () => {
    if (logs.length === 0) {
      alert('No records to download');
      return;
    }

    const headers = ['Document ID', 'Document Type', 'Extracted Date', 'Confidence Score', 'Status', 'Extracted Name'];
    const rows = logs.map(log => [
      log.id,
      log.document_type.toUpperCase(),
      new Date(log.created_at).toLocaleDateString('en-IN'),
      log.confidence_score,
      log.validation_status.toUpperCase(),
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
    a.download = `verification-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const handleNextPage = () => {
    if ((pagination.skip + pagination.limit) < pagination.total) {
      const newPage = pagination.currentPage + 1;
      setPagination(prev => ({
        ...prev,
        skip: prev.skip + prev.limit,
        currentPage: newPage
      }));
    }
  };

  const handlePreviousPage = () => {
    if (pagination.skip > 0) {
      const newPage = pagination.currentPage - 1;
      setPagination(prev => ({
        ...prev,
        skip: Math.max(0, prev.skip - prev.limit),
        currentPage: newPage
      }));
    }
  };

  const handlePageClick = (page) => {
    const newSkip = (page - 1) * pagination.limit;
    setPagination(prev => ({
      ...prev,
      skip: newSkip,
      currentPage: page
    }));
  };

  const maxPages = Math.ceil(pagination.total / pagination.limit);
  const pageNumbers = [];
  const startPage = Math.max(1, pagination.currentPage - 2);
  const endPage = Math.min(maxPages, pagination.currentPage + 2);
  
  for (let i = startPage; i <= endPage; i++) {
    pageNumbers.push(i);
  }

  return (
    <div className="verification-logs-wrapper">
      {/* Header Section */}
      <div className="logs-header-section">
        <div className="header-left">
          <h1 className="page-title">Verification History</h1>
        </div>
        <div className="header-right">
          <div className="sort-dropdown">
            <label htmlFor="sortBy">Sort by</label>
            <select 
              id="sortBy"
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="latest">Latest</option>
              <option value="oldest">Oldest</option>
            </select>
          </div>
          <button onClick={handleDownloadCSV} className="btn-download">
            Download as ▼
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-container">
          <div className="spinner"></div>
          <p>Loading verification history...</p>
        </div>
      )}

      {/* Error State */}
      {error && (
        <div className="error-container">
          <p className="error-text">⚠️ {error}</p>
          <button onClick={fetchLogs} className="btn-retry">Retry</button>
        </div>
      )}

      {/* Empty State */}
      {!loading && !error && logs.length === 0 && (
        <div className="empty-container">
          <p className="empty-text">No verification records found</p>
        </div>
      )}

      {/* Main Table */}
      {!loading && !error && logs.length > 0 && (
        <>
          <div className="table-wrapper">
            <table className="verification-table">
              <thead>
                <tr>
                  <th className="checkbox-col">
                    <input type="checkbox" />
                  </th>
                  <th className="doc-id-col">Document ID</th>
                  <th className="doc-type-col">Document Type</th>
                  <th className="date-col">Extracted Date</th>
                  <th className="confidence-col">Confidence</th>
                  <th className="status-col">Status</th>
                  <th className="action-col">Action</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((log, index) => (
                  <tr key={log.id} className="table-row">
                    <td className="checkbox-col">
                      <input type="checkbox" />
                    </td>
                    <td className="doc-id-col">
                      <span className="id-link">ID: {log.id}</span>
                      <button className="copy-btn" title="Copy ID">📋</button>
                    </td>
                    <td className="doc-type-col">
                      <span className="doc-type-pill">{log.document_type.toUpperCase()}</span>
                    </td>
                    <td className="date-col">
                      {new Date(log.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        year: 'numeric'
                      })}
                    </td>
                    <td className="confidence-col">
                      <div className="confidence-score-wrapper">
                        <span className="confidence-value">{log.confidence_score}</span>
                      </div>
                    </td>
                    <td className="status-col">
                      <span 
                        className="status-badge"
                        style={{ 
                          backgroundColor: getStatusColor(log.validation_status),
                          color: 'white'
                        }}
                      >
                        {log.validation_status.charAt(0).toUpperCase() + log.validation_status.slice(1)}
                      </span>
                    </td>
                    <td className="action-col">
                      <button 
                        onClick={(e) => handleViewDetails(log, e)}
                        className="action-btn-view"
                        title="View details"
                      >
                        👁️ View
                      </button>
                      <button className="action-menu" title="More options">⋮</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          <div className="pagination-section">
            <button 
              onClick={handlePreviousPage}
              disabled={pagination.currentPage === 1}
              className="btn-pagination prev"
            >
              ❮ Previous
            </button>
            <div className="page-numbers">
              {pageNumbers.map(page => (
                <button
                  key={page}
                  onClick={() => handlePageClick(page)}
                  className={`page-btn ${page === pagination.currentPage ? 'active' : ''}`}
                >
                  {page}
                </button>
              ))}
              {endPage < maxPages && <span className="page-ellipsis">...</span>}
            </div>
            <button 
              onClick={handleNextPage}
              disabled={pagination.currentPage === maxPages}
              className="btn-pagination next"
            >
              Next ❯
            </button>
          </div>
        </>
      )}

      {/* Details Modal */}
      {showDetails && selectedLog && (
        <div className={`modal-overlay ${showDetails ? 'active' : ''}`} onClick={handleCloseDetails}>
          <div className="modal-box" onClick={e => e.stopPropagation()}>
            <div className="modal-header-bar">
              <h2>Document Details</h2>
              <button className="modal-close-btn" onClick={handleCloseDetails}>&times;</button>
            </div>
            
            <div className="modal-content-area">
              <div className="details-section">
                <h3>Document Information</h3>
                <div className="detail-row">
                  <div className="detail-cell">
                    <label>Document ID</label>
                    <span>#{selectedLog.id}</span>
                  </div>
                  <div className="detail-cell">
                    <label>Document Type</label>
                    <span>{selectedLog.document_type.toUpperCase()}</span>
                  </div>
                </div>
                <div className="detail-row">
                  <div className="detail-cell">
                    <label>Confidence Score</label>
                    <span>{selectedLog.confidence_score}</span>
                  </div>
                  <div className="detail-cell">
                    <label>Validation Status</label>
                    <span style={{
                      color: getStatusColor(selectedLog.validation_status),
                      fontWeight: '600'
                    }}>
                      {selectedLog.validation_status.toUpperCase()}
                    </span>
                  </div>
                </div>
                <div className="detail-row">
                  <div className="detail-cell">
                    <label>Extraction Date & Time</label>
                    <span>
                      {new Date(selectedLog.created_at).toLocaleDateString('en-IN', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })} at {new Date(selectedLog.created_at).toLocaleTimeString('en-IN')}
                    </span>
                  </div>
                </div>
              </div>

              <div className="details-section">
                <h3>Extracted Data</h3>
                <div className="detail-row">
                  {selectedLog.extracted_data?.full_name && (
                    <div className="detail-cell">
                      <label>Full Name</label>
                      <span>{selectedLog.extracted_data.full_name}</span>
                    </div>
                  )}
                  {selectedLog.extracted_data?.id_number && (
                    <div className="detail-cell">
                      <label>{selectedLog.document_type.toUpperCase()} Number</label>
                      <span className="monospace">{selectedLog.extracted_data.id_number}</span>
                    </div>
                  )}
                </div>
                <div className="detail-row">
                  {selectedLog.extracted_data?.date_of_birth && (
                    <div className="detail-cell">
                      <label>Date of Birth</label>
                      <span>{selectedLog.extracted_data.date_of_birth}</span>
                    </div>
                  )}
                  {selectedLog.extracted_data?.gender && (
                    <div className="detail-cell">
                      <label>Gender</label>
                      <span>{selectedLog.extracted_data.gender}</span>
                    </div>
                  )}
                </div>
                {selectedLog.extracted_data?.phone && (
                  <div className="detail-row full">
                    <div className="detail-cell">
                      <label>Phone</label>
                      <span className="monospace">{selectedLog.extracted_data.phone}</span>
                    </div>
                  </div>
                )}
                {selectedLog.extracted_data?.address && (
                  <div className="detail-row full">
                    <div className="detail-cell">
                      <label>Address</label>
                      <span>{selectedLog.extracted_data.address}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className="modal-footer-area">
              <button onClick={handleCloseDetails} className="btn-modal-close">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default VerificationLogsPage;
