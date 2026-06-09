import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../../environments/environment';

@Component({
  selector: 'app-admin',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="card">
      <h2>Admin Panel - User Management</h2>
      <p>User management functionality would be implemented here.</p>
    </div>
  `
})
export class AdminComponent implements OnInit {
  constructor(private http: HttpClient) {}

  ngOnInit(): void {
    // Admin functionality can be expanded here
  }
}

