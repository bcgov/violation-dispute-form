import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AdminComponent } from 'app/admin/admin.component';
import { AuthGuard } from 'app/guards/auth-guard.component';

const routes: Routes = [
  {
    path: 'admin',
    component: AdminComponent,
    canActivate: [AuthGuard],
    data: {
      title: 'New Responses'
    }
  },
  {
    path: 'admin/new-responses',
    component: AdminComponent,
    canActivate: [AuthGuard],
    data: {
      title: 'New Responses'
    }
  },
  {
    path: 'admin/archive',
    component: AdminComponent,
    canActivate: [AuthGuard],
    data : {
      title: 'Archive'
    }
  },
  {
    path: 'admin/contact',
    component: AdminComponent,
    canActivate: [AuthGuard]
  }
];

@NgModule({
  imports: [RouterModule, RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminRoutingModule { }
