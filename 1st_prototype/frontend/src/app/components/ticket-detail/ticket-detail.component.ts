import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { TicketService, Ticket } from '../../services/ticket.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-ticket-detail',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div *ngIf="ticket">
      <div class="card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
          <h2>{{ ticket.title }}</h2>
          <a routerLink="/tickets" class="btn btn-secondary">Back to List</a>
        </div>
        
        <div style="margin-top: 20px;">
          <p><strong>Status:</strong> {{ ticket.status.replace('_', ' ') }}</p>
          <p><strong>Category:</strong> {{ ticket.category }}</p>
          <p><strong>Priority:</strong> <span class="badge badge-{{ ticket.priority }}">{{ ticket.priority }}</span></p>
          <p><strong>Created:</strong> {{ ticket.created_at | date:'medium' }}</p>
          <p><strong>Description:</strong></p>
          <p style="background: #f8f9fa; padding: 15px; border-radius: 4px;">{{ ticket.description }}</p>
        </div>
      </div>
      
      <div *ngIf="canEdit" class="card">
        <h3>Update Ticket</h3>
        <div *ngIf="error" class="alert alert-error">{{ error }}</div>
        <div *ngIf="success" class="alert alert-success">{{ success }}</div>
        
        <form (ngSubmit)="onUpdate()">
          <div class="form-group">
            <label>Status</label>
            <select [(ngModel)]="updateData.status" name="status">
              <option value="open">Open</option>
              <option value="in_progress">In Progress</option>
              <option value="resolved">Resolved</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          
          <div class="form-group">
            <label>Resolution Notes</label>
            <textarea [(ngModel)]="updateData.resolution_notes" name="resolution_notes"></textarea>
          </div>
          
          <button type="submit" class="btn btn-primary" [disabled]="loading">
            {{ loading ? 'Updating...' : 'Update Ticket' }}
          </button>
        </form>
      </div>
    </div>
    
    <div *ngIf="!ticket" class="card">
      <p>Loading ticket...</p>
    </div>
  `
})
export class TicketDetailComponent implements OnInit {
  ticket: Ticket | null = null;
  updateData = {
    status: undefined as any,
    resolution_notes: ''
  };
  error = '';
  success = '';
  loading = false;
  canEdit = false;

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private ticketService: TicketService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id');
    if (id) {
      this.loadTicket(id);
      this.authService.currentUser$.subscribe(user => {
        if (user) {
          this.canEdit = user.role !== 'end_user';
        }
      });
    }
  }

  loadTicket(id: string): void {
    this.ticketService.getTicket(id).subscribe({
      next: (ticket) => {
        this.ticket = ticket;
        this.updateData.status = ticket.status;
        this.updateData.resolution_notes = ticket.resolution_notes || '';
      },
      error: (err) => {
        console.error('Error loading ticket:', err);
      }
    });
  }

  onUpdate(): void {
    if (!this.ticket) return;
    
    this.loading = true;
    this.error = '';
    this.success = '';
    
    const updates: any = {};
    if (this.updateData.status) updates.status = this.updateData.status;
    if (this.updateData.resolution_notes) updates.resolution_notes = this.updateData.resolution_notes;
    
    this.ticketService.updateTicket(this.ticket.id, updates).subscribe({
      next: (updatedTicket) => {
        this.ticket = updatedTicket;
        this.success = 'Ticket updated successfully!';
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error?.detail || 'Failed to update ticket';
        this.loading = false;
      }
    });
  }
}

