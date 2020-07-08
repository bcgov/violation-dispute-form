import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { AdminRoutingModule } from './admin-routing.module';
import { AdminComponent } from './admin.component';
import { NgxDatatableModule } from '@swimlane/ngx-datatable';
import { NgbModule } from '@ng-bootstrap/ng-bootstrap';
import { ModalDelete } from "./modal-delete";

@NgModule({
  imports: [
    CommonModule,
    AdminRoutingModule,
    NgxDatatableModule,
    NgbModule
  ],
  declarations: [AdminComponent, ModalDelete]
})
export class AdminModule { }
