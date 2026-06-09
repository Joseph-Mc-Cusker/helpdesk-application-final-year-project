import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <header style="background: #007bff; color: white; padding: 15px 0; margin-bottom: 20px;">
      <div class="container" style="display: flex; justify-content: space-between; align-items: center;">
        <h1 style="margin: 0; font-size: 24px;">
          <a routerLink="/dashboard" style="color: white; text-decoration: none;">Helpdesk System</a>
        </h1>
        <nav style="display: flex; gap: 20px; align-items: center;">
          <ng-container *ngIf="authService.isAuthenticated()">
            <span *ngIf="authService.currentUser$ | async as user" style="margin-right: 10px;">
              {{ user.full_name }} ({{ user.role | titlecase }})
            </span>
            <a routerLink="/dashboard" style="color: white; text-decoration: none;">Dashboard</a>
            <a routerLink="/tickets" style="color: white; text-decoration: none;">My Tickets</a>
            <a routerLink="/tickets/create" style="color: white; text-decoration: none;">New Ticket</a>
            <a *ngIf="(authService.currentUser$ | async)?.role !== 'end_user'" 
               routerLink="/kanban" style="color: white; text-decoration: none;">Kanban</a>
            <a *ngIf="(authService.currentUser$ | async)?.role === 'administrator'" 
               routerLink="/admin" style="color: white; text-decoration: none;">Admin</a>
            <button (click)="logout()" class="btn" style="background: rgba(255,255,255,0.2); color: white; border: 1px solid white;">
              Logout
            </button>
          </ng-container>
        </nav>
      </div>
    </header>
  `
})
export class HeaderComponent {
  constructor(public authService: AuthService) {}

  logout(): void {
    this.authService.logout();
    window.location.href = '/login';
  }
}

