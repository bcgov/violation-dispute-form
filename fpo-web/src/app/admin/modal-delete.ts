import { Component, ViewChild } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { TicketResponseContent } from 'app/interfaces/admin_interfaces';


@Component({
    selector: 'modal-delete',
    templateUrl: './modal-delete.html'
})
export class ModalDelete {
    closeResult = '';
    private currentTicket: TicketResponseContent = null;
    
    @ViewChild('content', {static: false}) private content;

    constructor(private modalService: NgbModal) { }

    open(ticket: TicketResponseContent) : Promise<any> {
        this.currentTicket = ticket;
        return this.modalService.open(this.content, { ariaLabelledBy: 'modal-basic-title' }).result
    }
}
