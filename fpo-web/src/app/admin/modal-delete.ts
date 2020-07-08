import { Component, ViewChild } from '@angular/core';
import { NgbModal, ModalDismissReasons } from '@ng-bootstrap/ng-bootstrap';


@Component({
    selector: 'modal-delete',
    templateUrl: './modal-delete.html'
})
export class ModalDelete {
    closeResult = '';
    
    @ViewChild('content', {static: false}) private content;

    constructor(private modalService: NgbModal) { }

    open() {
        this.modalService.open(this.content, { ariaLabelledBy: 'modal-basic-title' }).result.then((result) => {
            this.closeResult = `Closed with: ${result}`;
            console.log(this.closeResult)
        }, (reason) => {
            this.closeResult = `Dismissed ${this.getDismissReason(reason)}`;
            console.log(this.closeResult);
        });
    }


    private getDismissReason(reason: any): string {
        if (reason === ModalDismissReasons.ESC) {
            return 'by pressing ESC';
        }
        else if (reason === ModalDismissReasons.BACKDROP_CLICK) {
            return 'by clicking on a backdrop';
        }
        else {
            return `with: ${reason}`;
        }
    }
}
