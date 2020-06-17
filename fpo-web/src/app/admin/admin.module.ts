import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { NgbDropdownModule, NgbDatepickerModule } from '@ng-bootstrap/ng-bootstrap';
import { AdminRoutingModule } from './admin-routing.module';
import { AdminComponent } from './admin.component';
import { AdminDataService } from './admin-data.service';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';

@NgModule({
  imports: [
    CommonModule,
    AdminRoutingModule,
    NgxDatatableModule,
    NgbDropdownModule,
    NgbDatepickerModule
  ],
  declarations: [AdminComponent]
})
export class AdminModule { }
