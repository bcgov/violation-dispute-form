import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AdminRoutingModule } from './admin-routing.module';
import { AdminComponent } from './admin.component';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ActivateGuard } from './activate-guard.component';

@NgModule({
  imports: [
    CommonModule,
    AdminRoutingModule,
    NgxDatatableModule,
    NgbModule
  ],
  providers: [ActivateGuard],
  declarations: [AdminComponent]
})
export class AdminModule { }
