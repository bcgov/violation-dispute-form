import { Component, Input, OnInit, OnDestroy } from "@angular/core";
import { ActivatedRoute, Router } from "@angular/router";
import { BehaviorSubject } from "rxjs";
import * as Survey from "survey-angular";
import * as showdown from "showdown";
import { GeneralDataService } from "../general-data.service";
import { GlossaryService } from "../glossary/glossary.service";
import { InsertService } from "../insert/insert.service";
import { addQuestionTypes } from "./question-types";
import { RecaptchaModule, RecaptchaFormsModule } from "ng-recaptcha";
import { HttpClient } from "@angular/common/http";
import Inputmask from 'inputmask';
import * as widgets from 'surveyjs-widgets';
@Component({
  selector: "app-survey-view",
  templateUrl: "./survey.component.html",
  styleUrls: ["./survey.component.scss"],
})
export class SurveyComponent implements OnInit, OnDestroy {
  private _active = false;
  private _jsonData: any;
  private _ready = false;
  private _lastSavedData: any;
  @Input() cacheName: string;
  @Input() onComplete: Function;
  @Input() surveyPath: string;
  @Input() initialMode: string;
  public pdfId: number;
  public cacheLoadTime: any;
  public cacheKey: string;
  public recaptchaKey: string;
  public recaptchaResponse: string;
  public submitError: string;
  public submitSuccess: string;
  public surveyCompleted = false;
  public surveyMode = "edit";
  public surveyModel: Survey.SurveyModel;
  public onPageUpdate: BehaviorSubject<
    Survey.SurveyModel
  > = new BehaviorSubject<Survey.SurveyModel>(null);
  public error: string;
  public loading = true;
  private useMarkdown = true;
  private useLocalCache = false;
  private disableCache = false;
  private markdownConverter: any;
  private showMissingTerms = true;
  private missingRequired = true;
  private prevPageIndex = null;
  private surveyCollection = "default";

  constructor(
    private dataService: GeneralDataService,
    private http: HttpClient,
    private insertService: InsertService,
    private glossaryService: GlossaryService,
    private _router: Router,
    private _route: ActivatedRoute
  ) {}

  ngOnInit() {
    if (this.initialMode) {
      this.surveyMode = this.initialMode;
    }
    this.initSurvey();
    this.glossaryService.onLoaded(() => {
      this._route.params.subscribe((params) => {
        this.cacheKey = params.id || null;
      });
      this.loadSurvey(true);
    });
    this._active = true;
    // FIXME - disabled: this.autoSave(true);
    this.fetchRecaptchaKey();
    this.dataService.currentValue.subscribe(pdfId => this.pdfId = pdfId)
  }

  initSurvey() {
    addQuestionTypes(Survey);
    Survey.defaultBootstrapCss.page.root = "sv_page";
    Survey.defaultBootstrapCss.pageDescription = "sv_page_description";
    Survey.defaultBootstrapCss.page.description = "sv_page_description";
    Survey.defaultBootstrapCss.pageTitle = "sv_page_title";
    Survey.defaultBootstrapCss.page.title = "sv_page_title";
    Survey.defaultBootstrapCss.navigationButton = "btn btn-primary";
    Survey.defaultBootstrapCss.question.title = "sv_q_title";
    Survey.defaultBootstrapCss.question.description = "sv_q_description";
    Survey.defaultBootstrapCss.panel.description = "sv_p_description";
    Survey.defaultBootstrapCss.matrixdynamic.button = "btn btn-primary";
    Survey.defaultBootstrapCss.paneldynamic.button = "btn btn-primary";
    Survey.defaultBootstrapCss.paneldynamic.root = "sv_p_dynamic";
    Survey.defaultBootstrapCss.checkbox.item = "sv-checkbox";
    Survey.defaultBootstrapCss.checkbox.controlLabel = "sv-checkbox-label";
    Survey.defaultBootstrapCss.checkbox.materialDecorator = "";
    Survey.defaultBootstrapCss.radiogroup.item = "sv-radio";
    Survey.defaultBootstrapCss.radiogroup.controlLabel = "sv-checkbox-label";
    Survey.defaultBootstrapCss.radiogroup.materialDecorator = "";
    Survey.StylesManager.applyTheme("bootstrap");
    widgets.inputmask(Survey);
  }

  ngOnDestroy() {
    this._active = false;
  }

  autoSave(init?) {
    if (!this._active) return;
    if (!init) {
      this.saveCache(true);
    }
    setTimeout(() => this.autoSave(), 120000);
  }

  get surveyJson() {
    return this._jsonData;
  }

  @Input("surveyJson")
  set surveyJson(value) {
    this._jsonData = value;
    this.loadSurvey();
  }

  loadSurvey(ready?) {
    if (ready) this._ready = ready;
    if (this._jsonData) {
      this.loading = false;
      if (this._ready && !this.surveyModel) {
        this.renderSurvey();
      }
    } else if (this.surveyPath) {
      this.dataService.loadJson(this.surveyPath).then((data) => {
        this.surveyJson = data;
      }); // .catch( (err) => ...)
    }
    // else this.error = 'Missing survey definition';
  }

  async renderSurvey() {
    const surveyModel = new Survey.Model(this._jsonData);
    surveyModel.commentPrefix = "Comment";
    surveyModel.showQuestionNumbers = "off";
    surveyModel.showNavigationButtons = false;

    // Create showdown markdown converter
    if (this.useMarkdown) {
      this.markdownConverter = new showdown.Converter({
        noHeaderId: true,
      });
      surveyModel.onTextMarkdown.add((survey, options) => {
        let str = this.markdownConverter.makeHtml(options.text);
        // remove root paragraph <p></p>
        const m = str.match(/^<p>(.*)<\/p>$/);
        if (m) {
          str = m[1];
        }
        // convert <code> into glossary tags
        str = str.replace(/<code>(.*?)<\/code>/g, (wholeMatch, m1) => {
          if (this.glossaryService.hasTerm(m1)) {
            // note: m1 is already html format
            return (
              '<a href="#" class="glossary-link" data-glossary="' +
              m1 +
              '">' +
              m1 +
              "</a>"
            );
          }
          if (this.showMissingTerms) {
            return "<code>" + m1 + "</code>";
          }
          return m1;
        });
        options.html = str;
      });
    }

    surveyModel.onComplete.add((sender, options) => {
      this.surveyCompleted = true;
      this.surveyMode = "print";
      //sif (!this.disableCache) this.saveCache();
      if (this.onComplete) this.onComplete(sender.data);
      this.onPageUpdate.next(sender);
      this.submitForm(sender.data);

    });
    surveyModel.onCurrentPageChanged.add((sender, options) => {
      this.onPageUpdate.next(sender);
      if (!this.disableCache && this.prevPageIndex !== sender.currentPageNo) {
        this.saveCache();
      }
      this.prevPageIndex = sender.currentPageNo;
    });
    surveyModel.onPageVisibleChanged.add((sender, options) => {
      this.onPageUpdate.next(sender);
    });
    surveyModel.onAfterRenderQuestion.add((sender, options) => {
      this.glossaryService.registerTargets(options.htmlElement);
    });
    surveyModel.onValueChanged.add((sender, options) => {
      this.evalProgress();
    });

    this.surveyModel = surveyModel;
    Survey.SurveyNG.render("surveyElement", { model: surveyModel });


    // update sidebar
    this.onPageUpdate.next(surveyModel);

    // fetch previous survey results
    if (!this.disableCache) this.loadCache();
  }

  get isLoaded(): boolean {
    return !!this.surveyModel;
  }

  get isFirstPage(): boolean {
    return this.surveyModel ? this.surveyModel.isFirstPage : false;
  }

  get isLastPage(): boolean {
    return this.surveyModel ? this.surveyModel.isLastPage : false;
  }

  changePage(pageNo: number) {
    this.surveyModel.currentPageNo = pageNo;
    if (this.surveyMode !== "edit") this.changeMode("edit");
  }

  changeMode(mode: string) {
    this.surveyMode = mode;
    if (mode === "print") {
      this.complete();
    } else {
      if (this.onComplete) this.onComplete(null);
    }
  }

  prevPage() {
    this.surveyModel.prevPage();
  }

  nextPage() {
    this.surveyModel.nextPage();
  }

  get recaptchaRequired(): boolean {
    return !!this.recaptchaKey;
  }

  get canComplete(): boolean {
    // FIXME include status of survey completion
    return !this.recaptchaRequired || !!this.recaptchaResponse && !this.missingRequired ;
  }

  get displayRecaptcha(): boolean {
    return !this.missingRequired;
  }

  fetchRecaptchaKey() {
    const url = this.dataService.getApiUrl("submit-form/");
    this.dataService.loadJson(url).then((rs) => {
      console.log(rs);
      if (rs && "key" in rs) {
        this.recaptchaKey = (rs as any).key;
      }
    });
  }

  // getting captchaResponse and enabling Complete button when captchaResponse is not blank
  resolvedCaptcha(captchaResponse: string) {
    this.recaptchaResponse = captchaResponse;
  }

  submitForm(data: any) {
    // This is horrendous.
    let form
    if (
      (data.continueDispute == 'y' &&
      data.disputeType == 'fineAmount' &&
      data.disputeInWriting == 'y')
        ||
      (data.continueDispute == 'n' &&
      data.moreTimeToPay1 == 'y'
      )
    ) {
      form = "violation-ticket-statement-and-written-reasons"; 
    } else {
      form = "notice-to-disputant-response";
    }

    const url = this.dataService.getApiUrl(`submit-form/?name=${form}`);
    const opts = this.recaptchaResponse
      ? { headers: { "X-CAPTCHA-RESPONSE": this.recaptchaResponse } }
      : undefined;
    this.http
      .post(url, data, { responseType: "json", ...opts })
      .toPromise()
      .then(
        (rs) => {
          console.log("submitted form successfully", rs);
          if(rs && "pdf-id" in rs) {
            this.pdfId = rs["pdf-id"];
            this.dataService.changePdfId(this.pdfId)
          }
        },
        (err) => {
          console.log("form submission failed", err);
        }
      );
  }

  complete() {
    this.surveyModel.completeLastPage();
  }

  resetCache() {
    if (this.surveyModel) {
      this.prevPageIndex = 0;
      this.surveyCompleted = false;
      this.surveyModel.data = {};
      this.surveyModel.currentPageNo = 0;
    }
    this.dataService.clearSurveyResult(
      this.surveyCollection,
      this.cacheName,
      this.cacheKey,
      this.useLocalCache
    );
    this.cacheLoadTime = null;
    this.cacheKey = null;
  }

  loadCache() {
    if (this.cacheKey) {
      this.dataService
        .loadSurveyResult(
          this.surveyCollection,
          this.cacheName,
          this.cacheKey,
          this.useLocalCache
        )
        .then(this.doneLoadCache.bind(this));
    } else {
      this.surveyModel.data = {};
    }
  }

  doneLoadCache(response) {
    if (response && response.accept_terms) {
      this._router.navigate(["/prv/status"]);
    } else if (response && response.result) {
      const cache = response.result;
      if (cache.data) {
        const prevPg = this.surveyModel.currentPageNo;
        this.surveyCompleted = cache.completed || false;
        this.prevPageIndex = cache.page || 0;
        this.surveyModel.currentPageNo = this.prevPageIndex;
        this.surveyModel.data = cache.data;
        this.cacheLoadTime = cache.time;
        this.cacheKey = response.id || response.key;
        if (this.surveyMode === "print" && this.surveyCompleted)
          this.complete();
        else if (prevPg === this.surveyModel.currentPageNo)
          this.onPageUpdate.next(this.surveyModel);
      }
    }
  }

  saveCache(auto?: boolean) {
    const cache = {
      time: new Date().getTime(),
      data: this.surveyModel.data,
      page: this.surveyModel.currentPageNo,
      completed: this.surveyCompleted,
    };
    const cmpCache = JSON.stringify(cache.data);
    if (auto && cmpCache === this._lastSavedData) {
      return;
    }
    this._lastSavedData = cmpCache;
    this.dataService
      .saveSurveyResult(
        this.surveyCollection,
        this.cacheName,
        cache,
        this.cacheKey,
        this.useLocalCache
      )
      .then(this.doneSaveCache.bind(this))
      .catch((err) => this.doneSaveCache(null, err));
  }

  doneSaveCache(response, err?) {
    if (response && response.status === "ok") {
      if (response.result) this.cacheLoadTime = response.result.time;
      this.cacheKey = response.id || response.key;
    }
  }

  evalProgress() {
    let missing = false;
    if (this.surveyModel) {
      const page = this.surveyModel.currentPage;
      if (page) {
        for (const panel of page.elements) {
          if (panel.isVisible) {
            for (const question of panel.elements) {
              if (question.isVisible && question.isRequired && question.isEmpty()) {
                missing = true;
                break;
              }
            }
          }
        }
      }
      // console.log('progress: ', this.surveyModel.getProgress(), done);
    }
    this.missingRequired = missing;
  }

  logout() {
    this.dataService.logout();
  }
}
