import React from 'react'

export function DataTable({ columns, data, onEdit, onDelete, loading }) {
  if (loading) {
    return (
      <div className="d-flex justify-content-center p-4">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="alert alert-info" role="alert">
        No records found
      </div>
    )
  }

  return (
    <div className="table-responsive">
      <table className="table table-striped table-hover">
        <thead className="table-light">
          <tr>
            {columns.map((col) => (
              <th key={col} scope="col">
                {col.charAt(0).toUpperCase() + col.slice(1)}
              </th>
            ))}
            <th scope="col">Actions</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.id}>
              {columns.map((col) => (
                <td key={`${row.id}-${col}`}>{row[col] || '-'}</td>
              ))}
              <td>
                <div className="btn-group btn-group-sm" role="group">
                  <button
                    onClick={() => onEdit(row)}
                    className="btn btn-outline-primary"
                  >
                    Edit
                  </button>
                  <button
                    onClick={() => onDelete(row.id)}
                    className="btn btn-outline-danger"
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
