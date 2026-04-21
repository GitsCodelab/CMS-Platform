/* SAP OpenUI5 Lite - Offline Component Library
   Version: 1.0.0
   Provides lightweight OpenUI5-like components for offline deployment */

// UI5 Component Factory
window.ui5 = window.ui5 || {
  components: {},
  utils: {}
};

// UI5 Table Component
ui5.components.Table = class {
  constructor(selector, options = {}) {
    this.element = document.querySelector(selector);
    this.data = options.data || [];
    this.columns = options.columns || [];
    this.selectable = options.selectable !== false;
    this.sortable = options.sortable !== false;
    this.pageSize = options.pageSize || 10;
    this.currentPage = 1;
    this.init();
  }

  init() {
    this.render();
    this.attachEvents();
  }

  render() {
    const table = document.createElement('table');
    table.className = 'ui5-table';
    
    // Header
    const thead = document.createElement('thead');
    const headerRow = document.createElement('tr');
    
    if (this.selectable) {
      const th = document.createElement('th');
      th.innerHTML = '<input type="checkbox" class="table-select-all">';
      th.style.width = '40px';
      headerRow.appendChild(th);
    }
    
    this.columns.forEach(col => {
      const th = document.createElement('th');
      th.textContent = col.label || col.key;
      if (this.sortable) {
        th.style.cursor = 'pointer';
        th.addEventListener('click', () => this.sort(col.key));
      }
      headerRow.appendChild(th);
    });
    
    thead.appendChild(headerRow);
    table.appendChild(thead);
    
    // Body
    const tbody = document.createElement('tbody');
    const start = (this.currentPage - 1) * this.pageSize;
    const end = start + this.pageSize;
    const pageData = this.data.slice(start, end);
    
    pageData.forEach((row, idx) => {
      const tr = document.createElement('tr');
      
      if (this.selectable) {
        const td = document.createElement('td');
        td.innerHTML = `<input type="checkbox" class="row-checkbox" data-id="${row.id}">`;
        td.style.width = '40px';
        tr.appendChild(td);
      }
      
      this.columns.forEach(col => {
        const td = document.createElement('td');
        const value = row[col.key];
        if (col.render) {
          td.innerHTML = col.render(value, row);
        } else {
          td.textContent = value;
        }
        tr.appendChild(td);
      });
      
      tbody.appendChild(tr);
    });
    
    table.appendChild(tbody);
    this.element.innerHTML = '';
    this.element.appendChild(table);
  }

  sort(column) {
    this.data.sort((a, b) => {
      if (a[column] < b[column]) return -1;
      if (a[column] > b[column]) return 1;
      return 0;
    });
    this.render();
  }

  attachEvents() {
    // Row selection
    this.element.querySelectorAll('.row-checkbox').forEach(cb => {
      cb.addEventListener('change', (e) => {
        this.onSelectionChange?.();
      });
    });
    
    // Select all
    const selectAll = this.element.querySelector('.table-select-all');
    if (selectAll) {
      selectAll.addEventListener('change', (e) => {
        this.element.querySelectorAll('.row-checkbox').forEach(cb => {
          cb.checked = e.target.checked;
        });
      });
    }
  }

  getSelectedRows() {
    const selected = [];
    this.element.querySelectorAll('.row-checkbox:checked').forEach(cb => {
      const id = cb.dataset.id;
      selected.push(this.data.find(d => d.id == id));
    });
    return selected;
  }

  addRow(row) {
    this.data.push(row);
    this.render();
  }

  updateRow(id, row) {
    const idx = this.data.findIndex(d => d.id == id);
    if (idx !== -1) {
      this.data[idx] = { ...this.data[idx], ...row };
      this.render();
    }
  }

  deleteRow(id) {
    this.data = this.data.filter(d => d.id != id);
    this.render();
  }
};

// UI5 Form Component
ui5.components.Form = class {
  constructor(selector, options = {}) {
    this.element = document.querySelector(selector);
    this.fields = options.fields || [];
    this.onSubmit = options.onSubmit;
    this.values = {};
    this.errors = {};
    this.init();
  }

  init() {
    this.render();
    this.attachEvents();
  }

  render() {
    const form = document.createElement('form');
    form.className = 'ui5-form';
    form.addEventListener('submit', (e) => e.preventDefault());
    
    this.fields.forEach(field => {
      const group = document.createElement('div');
      group.className = 'ui5-form-group';
      
      const label = document.createElement('label');
      label.className = field.required ? 'ui5-required' : '';
      label.textContent = field.label || field.name;
      group.appendChild(label);
      
      let input;
      if (field.type === 'textarea') {
        input = document.createElement('textarea');
        input.placeholder = field.placeholder || '';
        if (field.maxLength) input.maxLength = field.maxLength;
      } else if (field.type === 'select') {
        input = document.createElement('select');
        (field.options || []).forEach(opt => {
          const option = document.createElement('option');
          option.value = opt.value;
          option.textContent = opt.label;
          input.appendChild(option);
        });
      } else {
        input = document.createElement('input');
        input.type = field.type || 'text';
        input.placeholder = field.placeholder || '';
        if (field.maxLength) input.maxLength = field.maxLength;
      }
      
      input.name = field.name;
      input.className = 'ui5-input';
      input.id = `field-${field.name}`;
      
      // Character counter for textarea
      if (field.type === 'textarea' && field.maxLength) {
        const counter = document.createElement('small');
        counter.className = 'ui5-text-muted ui5-mt-1';
        counter.textContent = `0/${field.maxLength} characters`;
        counter.style.display = 'block';
        
        input.addEventListener('input', () => {
          counter.textContent = `${input.value.length}/${field.maxLength} characters`;
        });
        
        group.appendChild(input);
        group.appendChild(counter);
      } else {
        group.appendChild(input);
      }
      
      // Error message
      const error = document.createElement('div');
      error.className = 'ui5-alert ui5-alert-error ui5-mt-1';
      error.style.display = 'none';
      error.style.marginBottom = '0';
      group.appendChild(error);
      
      form.appendChild(group);
    });
    
    // Buttons
    const buttonGroup = document.createElement('div');
    buttonGroup.className = 'ui5-mt-3 ui5-d-flex ui5-gap-2';
    buttonGroup.style.justifyContent = 'flex-end';
    
    const submitBtn = document.createElement('button');
    submitBtn.type = 'submit';
    submitBtn.className = 'ui5-btn ui5-btn-primary';
    submitBtn.textContent = '💾 Submit';
    submitBtn.addEventListener('click', () => this.submit());
    
    const resetBtn = document.createElement('button');
    resetBtn.type = 'reset';
    resetBtn.className = 'ui5-btn ui5-btn-ghost';
    resetBtn.textContent = 'Cancel';
    resetBtn.addEventListener('click', () => this.reset());
    
    buttonGroup.appendChild(resetBtn);
    buttonGroup.appendChild(submitBtn);
    form.appendChild(buttonGroup);
    
    this.element.innerHTML = '';
    this.element.appendChild(form);
    this.form = form;
  }

  attachEvents() {
    this.fields.forEach(field => {
      const input = this.form.querySelector(`#field-${field.name}`);
      if (input) {
        input.addEventListener('change', () => {
          this.values[field.name] = input.value;
          this.clearError(field.name);
        });
        input.addEventListener('input', () => {
          this.values[field.name] = input.value;
        });
      }
    });
  }

  validate() {
    this.errors = {};
    let isValid = true;
    
    this.fields.forEach(field => {
      const input = this.form.querySelector(`#field-${field.name}`);
      const value = input.value.trim();
      
      if (field.required && !value) {
        this.setError(field.name, `${field.label || field.name} is required`);
        isValid = false;
      }
      
      if (field.minLength && value.length < field.minLength) {
        this.setError(field.name, `${field.label} must be at least ${field.minLength} characters`);
        isValid = false;
      }
      
      if (field.pattern && !new RegExp(field.pattern).test(value)) {
        this.setError(field.name, `${field.label} is invalid`);
        isValid = false;
      }
    });
    
    return isValid;
  }

  setError(fieldName, message) {
    this.errors[fieldName] = message;
    const input = this.form.querySelector(`#field-${fieldName}`);
    if (input) {
      input.style.borderColor = 'var(--sap-error)';
      input.style.backgroundColor = '#FFEBEE';
      
      const errorDiv = input.closest('.ui5-form-group').querySelector('.ui5-alert');
      if (errorDiv) {
        errorDiv.innerHTML = `⚠️ ${message}`;
        errorDiv.style.display = 'flex';
      }
    }
  }

  clearError(fieldName) {
    delete this.errors[fieldName];
    const input = this.form.querySelector(`#field-${fieldName}`);
    if (input) {
      input.style.borderColor = '';
      input.style.backgroundColor = '';
      
      const errorDiv = input.closest('.ui5-form-group').querySelector('.ui5-alert');
      if (errorDiv) {
        errorDiv.style.display = 'none';
      }
    }
  }

  submit() {
    if (this.validate()) {
      this.onSubmit?.(this.values);
    }
  }

  reset() {
    this.form.reset();
    this.values = {};
    this.errors = {};
    this.fields.forEach(field => this.clearError(field.name));
  }

  setValues(data) {
    Object.keys(data).forEach(key => {
      const input = this.form.querySelector(`#field-${key}`);
      if (input) {
        input.value = data[key];
        this.values[key] = data[key];
      }
    });
  }

  getValues() {
    return this.values;
  }
};

// UI5 Dialog Component
ui5.components.Dialog = class {
  constructor(options = {}) {
    this.title = options.title || 'Dialog';
    this.content = options.content || '';
    this.buttons = options.buttons || [];
    this.onClose = options.onClose;
  }

  show() {
    const overlay = document.createElement('div');
    overlay.className = 'ui5-dialog-overlay';
    
    const dialog = document.createElement('div');
    dialog.className = 'ui5-dialog';
    
    const header = document.createElement('div');
    header.className = 'ui5-dialog-header';
    header.innerHTML = `
      <h2 class="ui5-dialog-title">${this.title}</h2>
      <button class="ui5-dialog-close" type="button">&times;</button>
    `;
    
    const body = document.createElement('div');
    body.className = 'ui5-dialog-body';
    body.innerHTML = this.content;
    
    const footer = document.createElement('div');
    footer.className = 'ui5-dialog-footer';
    
    this.buttons.forEach(btn => {
      const button = document.createElement('button');
      button.className = `ui5-btn ${btn.class || 'ui5-btn-primary'}`;
      button.textContent = btn.text;
      button.addEventListener('click', () => {
        btn.action?.();
        this.close();
      });
      footer.appendChild(button);
    });
    
    dialog.appendChild(header);
    dialog.appendChild(body);
    dialog.appendChild(footer);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    
    // Close handlers
    const closeBtn = header.querySelector('.ui5-dialog-close');
    closeBtn.addEventListener('click', () => this.close());
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) this.close();
    });
    
    this.overlay = overlay;
  }

  close() {
    this.overlay?.remove();
    this.onClose?.();
  }
};

// UI5 Toast/Notification
ui5.components.Toast = class {
  static show(message, type = 'info', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `ui5-alert ui5-alert-${type}`;
    toast.style.position = 'fixed';
    toast.style.bottom = '20px';
    toast.style.right = '20px';
    toast.style.minWidth = '300px';
    toast.style.zIndex = '2000';
    
    const icons = {
      success: '✓',
      error: '⚠️',
      warning: '⚡',
      info: 'ℹ️'
    };
    
    toast.innerHTML = `<span>${icons[type]}</span><span>${message}</span>`;
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
};

// UI5 Utilities
ui5.utils.debounce = function(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
};

ui5.utils.formatDate = function(date) {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  });
};

ui5.utils.formatCurrency = function(value, currency = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency
  }).format(value);
};

console.log('✅ SAP OpenUI5 Lite loaded - Offline component library ready');
