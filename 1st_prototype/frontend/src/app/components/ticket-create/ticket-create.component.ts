import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterModule } from '@angular/router';
import { TicketService } from '../../services/ticket.service';

@Component({
  selector: 'app-ticket-create',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="card">
      <h2>Create New Ticket</h2>
      <div *ngIf="error" class="alert alert-error">{{ error }}</div>
      <div *ngIf="success" class="alert alert-success">{{ success }}</div>
      
      <form (ngSubmit)="onSubmit()">
        <div class="form-group">
          <label>Title *</label>
          <input type="text" [(ngModel)]="ticket.title" name="title" required>
        </div>
        
        <div class="form-group">
          <label>Category *</label>
          <select [(ngModel)]="ticket.category" name="category" required>
            <option value="">Select category</option>
            <option value="hardware">Hardware</option>
            <option value="software">Software</option>
            <option value="network">Network</option>
            <option value="email">Email</option>
            <option value="account">Account</option>
            <option value="other">Other</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Priority *</label>
          <select [(ngModel)]="ticket.priority" name="priority" required>
            <option value="low">Low</option>
            <option value="medium" selected>Medium</option>
            <option value="high">High</option>
            <option value="urgent">Urgent</option>
          </select>
        </div>
        
        <div class="form-group">
          <label>Description *</label>
          <textarea [(ngModel)]="ticket.description" name="description" required></textarea>
        </div>
        
        <button type="submit" class="btn btn-primary" [disabled]="loading">
          {{ loading ? 'Creating...' : 'Create Ticket' }}
        </button>
        <a routerLink="/tickets" class="btn btn-secondary" style="margin-left: 10px;">Cancel</a>
      </form>
    </div>
  `
})
export class TicketCreateComponent {
  ticket = {
    title: '',
    description: '',
    category: '',
    priority: 'medium' as 'low' | 'medium' | 'high' | 'urgent'
  };
  error = '';
  success = '';
  loading = false;

  constructor(
    private ticketService: TicketService,
    private router: Router
  ) {}

  onSubmit(): void {
    this.loading = true;
    this.error = '';
    this.success = '';
    
    this.ticketService.createTicket(this.ticket).subscribe({
      next: (ticket) => {
        this.success = 'Ticket created successfully!';
        setTimeout(() => {
          this.router.navigate(['/tickets', ticket.id]);
        }, 1500);
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to create ticket';
        this.loading = false;
      }
    });
  }
}

