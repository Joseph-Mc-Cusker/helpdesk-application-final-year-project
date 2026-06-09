import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardService, KanbanData } from '../../services/dashboard.service';

@Component({
  selector: 'app-kanban',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="card">
      <h2>Kanban Board</h2>
      <button (click)="loadKanban()" class="btn btn-secondary" style="margin-bottom: 20px;">Refresh</button>
      
      <div class="kanban-board" *ngIf="kanbanData">
        <div class="kanban-column">
          <h3>Open ({{ kanbanData.open.length }})</h3>
          <div *ngFor="let ticket of kanbanData.open" class="kanban-card">
            <h4>{{ ticket.title }}</h4>
            <p><strong>Priority:</strong> <span class="badge badge-{{ ticket.priority }}">{{ ticket.priority }}</span></p>
            <p><strong>Category:</strong> {{ ticket.category }}</p>
            <a [routerLink]="['/tickets', ticket.id]" class="btn btn-secondary" style="margin-top: 10px; padding: 5px 10px; font-size: 12px;">View</a>
          </div>
        </div>
        
        <div class="kanban-column">
          <h3>In Progress ({{ kanbanData.inprogress.length }})</h3>
          <div *ngFor="let ticket of kanbanData.inprogress" class="kanban-card">
            <h4>{{ ticket.title }}</h4>
            <p><strong>Priority:</strong> <span class="badge badge-{{ ticket.priority }}">{{ ticket.priority }}</span></p>
            <p><strong>Category:</strong> {{ ticket.category }}</p>
            <a [routerLink]="['/tickets', ticket.id]" class="btn btn-secondary" style="margin-top: 10px; padding: 5px 10px; font-size: 12px;">View</a>
          </div>
        </div>
        
        <div class="kanban-column">
          <h3>Resolved ({{ kanbanData.resolved.length }})</h3>
          <div *ngFor="let ticket of kanbanData.resolved" class="kanban-card">
            <h4>{{ ticket.title }}</h4>
            <p><strong>Priority:</strong> <span class="badge badge-{{ ticket.priority }}">{{ ticket.priority }}</span></p>
            <p><strong>Category:</strong> {{ ticket.category }}</p>
            <a [routerLink]="['/tickets', ticket.id]" class="btn btn-secondary" style="margin-top: 10px; padding: 5px 10px; font-size: 12px;">View</a>
          </div>
        </div>
        
        <div class="kanban-column">
          <h3>Closed ({{ kanbanData.closed.length }})</h3>
          <div *ngFor="let ticket of kanbanData.closed" class="kanban-card">
            <h4>{{ ticket.title }}</h4>
            <p><strong>Priority:</strong> <span class="badge badge-{{ ticket.priority }}">{{ ticket.priority }}</span></p>
            <p><strong>Category:</strong> {{ ticket.category }}</p>
            <a [routerLink]="['/tickets', ticket.id]" class="btn btn-secondary" style="margin-top: 10px; padding: 5px 10px; font-size: 12px;">View</a>
          </div>
        </div>
      </div>
    </div>
  `
})
export class KanbanComponent implements OnInit {
  kanbanData: KanbanData | null = null;

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.loadKanban();
  }

  loadKanban(): void {
    this.dashboardService.getKanbanData().subscribe({
      next: (data) => {
        this.kanbanData = data;
      },
      error: (err) => {
        console.error('Error loading kanban data:', err);
      }
    });
  }
}

