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
  public recaptchaKey: string;
  public recaptchaResponse: string;
  public inited = true;
  public feedback = { reason: '', from_name: '', from_email: '', comments: '', invalid: null };
  public failed = false;
  public sending = false;
  public sent = false;

  constructor(private dataService: GeneralDataService, private http: HttpClient,) { }

  ngOnInit() {
     //Hide footer detail.
    let footerDetail = <HTMLElement>document.querySelector(".footer-detail");
    footerDetail.style.display = "none";
    
    this.dataService.key.subscribe(recaptchaKey => this.recaptchaKey = recaptchaKey)
  }

  get canSend(): boolean {
    return !this.recaptchaRequired || !!this.recaptchaResponse;
  }

  get recaptchaRequired(): boolean {
    return !!this.recaptchaKey;
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

  resolvedCaptcha(captchaResponse: string) {
    this.recaptchaResponse = captchaResponse;
  }

  sendFeedback(evt) {
    if (evt) evt.preventDefault();
    if (this.sending) return;
    this.sending = true;
    this.sent = false;

    const fb = this.feedback;
    const valid = this.checkFeedback(fb);
    fb.invalid = valid ? null : 'required';
    if (!valid) {
      this.focusAlert('alert-required');
      this.sending = false;
      return;
    }

    const url = this.dataService.getApiUrl('feedback/');
    const opts = this.recaptchaResponse
      ? { headers: { "X-CAPTCHA-RESPONSE": this.recaptchaResponse } }
      : undefined;
    this.http
      .post(url, fb,{ responseType: "json", ...opts })
      .toPromise()
      .then(
        (rs) => {
          console.log(" feedback success", rs);
          this.sent = true;
          this.sending = false;
          this.focusAlert('alert-success');
          this.feedback = { reason: '', from_name: '', from_email: '', comments: '', invalid: null };
          grecaptcha.reset();
          this.recaptchaResponse ="";
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
