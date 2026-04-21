import React from 'react'

export function DataTable({ columns, data, onEdit, onDelete, loading }) {
  if (loading) {
    return (
      <div className="d-flex justify-content-center p-5">
        <div className="spinner-border" role="status" style={{ color: 'var(--sap-primary)', width: '3rem', height: '3rem' }}>
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="alert alert-info" role="alert" style={{ margin: '2rem 0' }}>
        <strong>📋 No Records Found</strong>
        <p style={{ marginBottom: 0, marginTop: '0.5rem' }}>No records are available to display at this time.</p>
      </div>
    )
  }

  return (
    <div style={{
      backgroundColor: '#FFFFFF',
      borderRadius: '4px',
      border: '1px solid var(--sap-border-light)',
      boxShadow: 'var(--sap-shadow)',
      overflow: 'hidden'
    }}>
      <div className="table-responsive" style={{ margin: 0 }}>
        <table className="table" style={{ marginBottom: 0 }}>
          <thead>
            <tr style={{
              backgroundColor: '#F0F0F0',
              borderBottom: '2px solid var(--sap-border)'
            }}>
              {columns.map((col) => (
                <th key={col} scope="col" style={{
                  padding: '1rem 0.75rem',
                  color: 'var(--sap-text)',
                  fontWeight: '600',
                  fontSize: '0.875rem',
                  textTransform: 'capitalize',
                  letterSpacing: '-0.3px',
                  whiteSpace: 'nowrap'
                }}>
                  {col.charAt(0).toUpperCase() + col.slice(1)}
                </th>
              ))}
              <th scope="col" style={{
                padding: '1rem 0.75rem',
                color: 'var(--sap-text)',
                fontWeight: '600',
                fontSize: '0.875rem',
                textAlign: 'center'
              }}>
                Actions
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((row, idx) => (
              <tr key={row.id} style={{
                backgroundColor: idx % 2 === 0 ? '#FFFFFF' : '#FAFAFA',
                borderBottom: '1px solid var(--sap-border-light)',
                transition: 'background-color 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.backgroundColor = '#E8F1F9'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.backgroundColor = idx % 2 === 0 ? '#FFFFFF' : '#FAFAFA'
              }}>
                {columns.map((col) => (
                  <td key={`${row.id}-${col}`} style={{
                    padding: '0.875rem 0.75rem',
                    color: 'var(--sap-text)',
                    fontSize: '0.875rem',
                    verticalAlign: 'middle'
                  }}>
                    {row[col] || '—'}
                  </td>
                ))}
                <td style={{
                  padding: '0.875rem 0.75rem',
                  textAlign: 'center'
                }}>
                  <div style={{ display: 'flex', gap: '0.5rem', justifyContent: 'center' }}>
                    <button
                      onClick={() => onEdit(row)}
                      className="btn"
                      
                      onMouseEnter={(e) => {
                        e.target.style.backgroundColor = 'var(--sap-primary-dark)'
                        e.target.style.transform = 'translateY(-1px)'
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.backgroundColor = 'var(--sap-primary)'
                        e.target.style.transform = 'translateY(0)'
                      }}
                    >
                      ✎ Edit
                    </button>
                    <button
                      onClick={() => onDelete(row.id)}
                      className="btn"
                      style={{
                        padding: '0.5rem 0.875rem',
                        backgroundColor: 'var(--sap-error)',
                        color: 'white',
                        border: 'none',
                        borderRadius: '4px',
                        fontSize: '0.75rem',
                        fontWeight: '500',
                        cursor: 'pointer',
                        transition: 'all 0.2s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.target.style.backgroundColor = '#c80e1f'
                        e.target.style.transform = 'translateY(-1px)'
                      }}
                      onMouseLeave={(e) => {
                        e.target.style.backgroundColor = 'var(--sap-error)'
                        e.target.style.transform = 'translateY(0)'
                      }}
                    >
                      🗑 Delete
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{
        padding: '1rem 0.75rem',
        backgroundColor: '#FAFAFA',
        borderTop: '1px solid var(--sap-border-light)',
        fontSize: '0.8125rem',
        color: 'var(--sap-text-muted)',
        textAlign: 'right'
      }}>
        Total Records: <strong style={{ color: 'var(--sap-text)' }}>{data.length}</strong>
      </div>
    </div>
  )
}
