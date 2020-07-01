import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AdminComponent } from 'app/admin/admin.component';
import { ActivateGuard } from 'app/admin/activate-guard.component';

const routes: Routes = [
  {
    path: 'admin',
    component: AdminComponent,
    canActivate: [ActivateGuard],
    data: {
      title: 'New Responses'
    }
  },
  {
    path: 'admin/new-responses',
    component: AdminComponent,
    canActivate: [ActivateGuard],
    data: {
      title: 'New Responses'
    }
  },
  {
    path: 'admin/archive',
    component: AdminComponent,
    canActivate: [ActivateGuard],
    data : {
      title: 'Archive'
    }
  },
  {
    path: 'admin/contact',
    component: AdminComponent,
    canActivate: [ActivateGuard]
  }
];

@NgModule({
  imports: [RouterModule, RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminRoutingModule { }
