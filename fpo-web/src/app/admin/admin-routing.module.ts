import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { AdminComponent } from 'app/admin/admin.component';
import { LoginComponent } from 'app/login/login.component';
import { AuthGuard } from 'app/guards/auth-guard.component';
import { ContactComponent } from '../contact/contact.component';
const routes: Routes = [
  {
    path: 'login',
    component: LoginComponent,
    data: {
      title: 'Login'
    }
  },
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
    path: 'contact',
    component: ContactComponent,
    canActivate: [AuthGuard]
  }
];

@NgModule({
  imports: [RouterModule, RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class AdminRoutingModule { }
