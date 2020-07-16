import { Component, OnInit } from "@angular/core";
import { ActivatedRoute } from "@angular/router";
import { GeneralDataService } from "app/general-data.service";
import { HttpClient } from "@angular/common/http";

@Component({
  selector: "app-contact-component",
  templateUrl: "./contact.component.html",
  styleUrls: ["./contact.component.scss"],
})
export class ContactComponent implements OnInit {
  //#region Variables & Constructor
  public loading = true;
  private _loginRedirect: string = null;



  inited = true;
  feedback = { reason: '', from_name: '', from_email: '', comments: '', invalid: null };
  failed = false;
  sending = false;
  sent = false;

  constructor(private _dataService: GeneralDataService, private http: HttpClient,) { }

  ngOnInit() {

  }

  checkFeedback(fb) {
    if (!fb.reason || !fb.from_name || !fb.from_email)
      return false;
    return true;
  }

  focusAlert(id) {
    setTimeout(() => {
      let alert = document.getElementById(id);
      if (alert) alert.focus();
    }, 50);
  }

  sendFeedback(evt) {
    if (evt) evt.preventDefault();
    if (this.sending) return;
    this.sending = true;
    this.sent = false;

    let fb = this.feedback;
    let valid = this.checkFeedback(fb);
    fb.invalid = valid ? null : 'required';
    if (!valid) {
      this.focusAlert('alert-required');
      this.sending = false;
      return;
    }

    let url = this._dataService.getApiUrl('feedback/');
    const data = fb
    this.http
      .post(url, data,)
      .toPromise()
      .then(
        (rs) => {
          console.log(" feedback success", rs);
          this.sent = true;
          this.sending = false;
          this.focusAlert('alert-success');
          this.feedback = { reason: '', from_name: '', from_email: '', comments: '', invalid: null };
        },
        (err) => {
          console.log("feedback submission failed", err);
          this.failed = true;
          this.sending = false;
          this.focusAlert('alert-error');
        }
      );

  }

}
