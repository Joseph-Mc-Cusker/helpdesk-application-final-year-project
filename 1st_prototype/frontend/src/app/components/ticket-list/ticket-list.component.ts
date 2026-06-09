import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { TicketService, Ticket } from '../../services/ticket.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-ticket-list',
  standalone: true,
  imports: [CommonModule, RouterModule, FormsModule],
  template: `
    <div class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>My Tickets</h2>
        <a routerLink="/tickets/create" class="btn btn-primary">Create New Ticket</a>
      </div>
      
      <div style="margin-bottom: 15px;">
        <label>Filter by Status: </label>
        <select [(ngModel)]="statusFilter" (change)="loadTickets()" style="margin-left: 10px; padding: 5px;">
          <option value="">All</option>
          <option value="open">Open</option>
          <option value="in_progress">In Progress</option>
          <option value="resolved">Resolved</option>
          <option value="closed">Closed</option>
        </select>
      </div>
      
      <table class="table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Title</th>
            <th>Category</th>
            <th>Priority</th>
            <th>Status</th>
            <th>Created</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr *ngFor="let ticket of tickets">
            <td>{{ ticket.id.substring(0, 8) }}</td>
            <td>{{ ticket.title }}</td>
            <td>{{ ticket.category }}</td>
            <td>
              <span class="badge badge-{{ ticket.priority }}">{{ ticket.priority }}</span>
            </td>
            <td>{{ ticket.status.replace('_', ' ') }}</td>
            <td>{{ ticket.created_at | date:'short' }}</td>
            <td>
              <a [routerLink]="['/tickets', ticket.id]" class="btn btn-secondary" style="padding: 5px 10px; font-size: 12px;">View</a>
            </td>
          </tr>
          <tr *ngIf="tickets.length === 0">
            <td colspan="7" style="text-align: center; padding: 20px;">No tickets found</td>
          </tr>
        </tbody>
      </table>
    </div>
  `
})
export class TicketListComponent implements OnInit {
  tickets: Ticket[] = [];
  statusFilter = '';

  constructor(
    private ticketService: TicketService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadTickets();
  }

  loadTickets(): void {
    this.ticketService.getTickets(this.statusFilter || undefined).subscribe({
      next: (tickets) => {
        this.tickets = tickets;
      },
      error: (err) => {
        console.error('Error loading tickets:', err);
      }
    });
  }
}

