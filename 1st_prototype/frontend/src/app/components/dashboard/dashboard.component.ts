import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { DashboardService, DashboardStats } from '../../services/dashboard.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="card">
      <h2>Dashboard</h2>
      <div *ngIf="stats" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-top: 20px;">
        <div style="text-align: center; padding: 20px; background: #f8f9fa; border-radius: 8px;">
          <h3 style="font-size: 36px; margin: 0; color: #007bff;">{{ stats.total }}</h3>
          <p style="margin: 5px 0 0 0; color: #666;">Total Tickets</p>
        </div>
        <div style="text-align: center; padding: 20px; background: #fff3cd; border-radius: 8px;">
          <h3 style="font-size: 36px; margin: 0; color: #856404;">{{ stats.open }}</h3>
          <p style="margin: 5px 0 0 0; color: #666;">Open</p>
        </div>
        <div style="text-align: center; padding: 20px; background: #d1ecf1; border-radius: 8px;">
          <h3 style="font-size: 36px; margin: 0; color: #0c5460;">{{ stats.in_progress }}</h3>
          <p style="margin: 5px 0 0 0; color: #666;">In Progress</p>
        </div>
        <div style="text-align: center; padding: 20px; background: #d4edda; border-radius: 8px;">
          <h3 style="font-size: 36px; margin: 0; color: #155724;">{{ stats.resolved }}</h3>
          <p style="margin: 5px 0 0 0; color: #666;">Resolved</p>
        </div>
        <div style="text-align: center; padding: 20px; background: #d1ecf1; border-radius: 8px;">
          <h3 style="font-size: 36px; margin: 0; color: #0c5460;">{{ stats.closed }}</h3>
          <p style="margin: 5px 0 0 0; color: #666;">Closed</p>
        </div>
      </div>
      <div *ngIf="!stats" style="text-align: center; padding: 40px;">
        <p>Loading dashboard statistics...</p>
      </div>
    </div>
    
    <div class="card">
      <h3>Quick Actions</h3>
      <div style="display: flex; gap: 10px; margin-top: 15px; flex-wrap: wrap;">
        <a routerLink="/tickets/create" class="btn btn-primary">Create New Ticket</a>
        <a routerLink="/tickets" class="btn btn-secondary">View All Tickets</a>
        <a *ngIf="(authService.currentUser$ | async)?.role !== 'end_user'" 
           routerLink="/kanban" class="btn btn-secondary">Kanban View</a>
      </div>
    </div>
  `
})
export class DashboardComponent implements OnInit {
  stats: DashboardStats | null = null;

  constructor(
    private dashboardService: DashboardService,
    public authService: AuthService
  ) {}

  ngOnInit(): void {
    this.loadStats();
  }

  loadStats(): void {
    this.dashboardService.getStats().subscribe({
      next: (stats) => {
        this.stats = stats;
      },
      error: (err) => {
        console.error('Error loading stats:', err);
      }
    });
  }
}

