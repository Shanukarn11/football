
from django.urls import path
from main import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path("noticeboard", views.noticeboard_home, name="noticeboard_home"),
    path("noticeboard/ikf-broadcast", views.ikf_broadcast_page, name="ikf_broadcast"),
    path("noticeboard/circular/<slug:slug>", views.official_circular_detail, name="official_circular_detail"),
    path("noticeboard/ikftrialresults/<slug:city_slug>/<slug:project_slug>/", views.trial_result_detail_page, name="trial_result_detail_page"),
    path("noticeboard/<slug:slug>", views.noticeboard_slug_router, name="noticeboard_slug"),
    path("api/noticeboard/trial-results/cities/", views.upcoming_trials_cities_api, name="noticeboard_trial_results_cities_api"),
    path("api/noticeboard/trial-results/detail/", views.trial_results_detail_api, name="noticeboard_trial_results_detail_api"),
    path("invictus-donations/", views.invictus_donations, name="invictus_donations"),
    path('invictusxOPJindal', views.invictus_home, name='invictus_home'),
    path('invictusxopjindal', views.invictus_home, name='invictus_home'),
    path('', views.home, name='home'),

    
    path('onboarding/', views.rep_onboarding, name='onboarding'),          
    path('rep-template/', views.rep_template, name='rep_template'),    
    path("lawyers/", views.lawyer_landing, name="lawyer_landing"),

    # 2) Grid page (All Lawyers)
    path("lawyers/all/", views.lawyer_index, name="lawyer_index"),

    # 3) Detail page
    path("lawyer/<slug:template_link>/", views.lawyer_detail, name="lawyer_detail"),

    path("level2scouts/", views.scout_landing, name="scout_landing"),
    path("level2scouts/all/", views.scout_index, name="scout_index"),
    path("level2scouts/<slug:slug>/", views.scout_detail, name="scout_detail"),
    
    path('past_trials', views.season1, name='season1'),
    path('season2', views.season2, name='season2'),
    path('scoutingcertification_', views.scoutingcertification, name='scoutingcertification'),
    path('Job/Apprenticeship', views.playabroad, name='playabroad'),
    path('ikf_workshop', views.workshops, name='ikf_workshop'),
    path('workshops', views.ikf_workshop, name='workshops'),
    path('ikftech/<str:lang>/', views.ikftech, name='ikftech'),

    path('ikf_aboutus', views.ikf_aboutus, name='ikf_aboutus'),
    path('team-behind-ikf', views.team_behind_ikf, name='team-behind-ikf'),
    path('mission-and-vision', views.mission_and_vision, name='mission-and-vision'),
    path('regional-execution-partners', views.regionalpartners, name='regionalpartners'),
    path('nationalpartners', views.nationalpartners, name='nationalpartners'),
    path('international-clubs-academies', views.internationalpartners, name='internationalpartners'),
    path('corporates', views.corporates, name='corporates'),
    path('indian-clubs-academies', views.clubs, name='clubs'),
    path("rep/all/", views.rep_index, name="rep_index"),
    path('donate', views.Donate, name='Donate'),
    path('donate/offline-claim', views.offline_donation_claim, name='offline_donation_claim'),
    path('donate/thank-you', views.donate_thank_you, name='donate_thank_you'),
    path('donate/<slug:slug>/', views.donate_project_detail, name='donate_project_detail'),
    path('Corporate', views.Associate_Corporates, name='Corporate'),
    path('Philanthropists', views.Associate_Philanthropists, name='Philanthropists'),
    path('PSUS', views.Associate_PSUS, name='PSUS'),

    path('workshopsreg', views.workshopsReg, name='workshopsreg'),
    path('associate_academy', views.Associate_Academy, name='associate_academy'),
    path('contact_us', views.Associate_Clubs, name='associate_clubs'),
    path('associate_tournamentorganizer', views.Associate_TournamentOrganizer, name='associate_tournamentorganizer'),

    path('Gallery', views.Photo_Gallery, name='Gallery'),
    path('Resources', views.ResourcesFun, name='Resources'),
    path('annual_impact', views.supported_by, name='supporters'),
    path('faces_of_change', views.international_alliance, name='international-alliance'),
    path('democratizing_the_dream', views.football_education, name='football-education'),
    path('woman-empowerment', views.woman_empowerment, name='woman-empowerment'),
    path('community-development', views.community_development, name='community-development'),
    path('north_east_rising', views.invest_social_impact, name='invest-social-impact'),
    path('sponsorship-opportunities', views.sponsorship_opportunities, name='sponsorship-opportunities'),
    
    path('donate/', views.invictus_donate, name='invictus_donate'),
    path('ikf-spotonn-announcement-en', views.ikf_spotonn_en, name='ikf-spotonn-announcement-en'),
    path('ikf-spotonn-announcement-hi', views.ikf_spotonn_hi, name='ikf-spotonn-announcement-hi'),

    path('ikf-center-of-excellence', views.ikf_center_of_excellence, name='ikf-center-of-excellence'),
    path('ikf-center-of-excellence/desportz', views.desportz_ikf_coe, name='desportz-ikf-coe'),
    path('ikf-center-of-excellence/imt-ghaziabad', views.imt_ghaziabad_ikf_coe, name='imt-ghaziabad-ikf-coe'),
    path('ikf-center-of-excellence/skss', views.skss_ikf_coe, name='skss-ikf-coe'),
    path('ikf-center-of-excellence/threelok', views.threelok_ikf_coe, name='threelok-ikf-coe'),

    path('ikf-dual-career-pathways', views.IKF_dual_career_pathways, name='ikf-dual-career-pathways'),
    path('ikf-videos', views.IKF_videos, name="ikf-videos"),
    path('ikf-news', views.IKF_news, name="ikf-news"),
    path('ikf-partners', views.IKF_Partners, name="ikf-partners"),
    path('ikf-winners', views.IKF_Winners, name="ikf-winners"),
    path('season5finals', views.Support_IKF, name="support-ikf"),
    path("rep/", views.rep_landing, name="rep_landing"),
    path("academy-partners/", views.academy_partners, name="academy-partners"),
    path('state-association-partners/', views.state_association_partners, name='state-association-partners'),
    path('state-association-partners/<slug:slug>/', views.state_association_partner_detail, name='state-association-partner-detail'),
    # ===== payments =====
    path('order', views.order, name='order'),
    path('payment', views.payment, name='payment'),
    path('save', views.save, name='save'),
    path('successpayment', views.successpayment, name='successpayment'),
    path('thankyou', views.thankyou, name='thankyou'),
    path('paymentstatus', views.paymentstatus, name='paymentstatus'),
    path('paymentpass', views.paymentpass, name='paymentpass'),
    path('paymentfail', views.paymentfail, name='paymentfail'),

    # ===== programs/pages =====
    path('ikf-as-scouting-partners', views.ikf_as_scouting_partners, name='ikf-as-scouting-partners'),
    path('Anaya-Goal', views.anaya_goal, name='anaya_goal'),
    path('un-certificate', views.un_certificate, name='un_certificate'),
    
    path("noc/<slug:code>/", views.noc_page, name="noc_page"),
    path('sponsordeck', views.sponsordeck, name='sponsordeck'),
    # path('calendar', views.calender, name='calender'),
    path('request_for_player', views.request_for_player, name='request_for_player'),
    path('field_of_dreams', views.career360, name='career360'),

    path('ikf_international_alliance', views.ikf_international_alliance, name='ikf_international_alliance'),
    path('scoutingcertification', views.discovery_call, name='discovery_call'),
    path('student_athlete_pathway', views.student_athlete_pathway, name='student_athlete_pathway'),
    path('scouts_on_wheels', views.professional_pathway, name='professional_pathway'),
    path('naari_shakti', views.naari_shakti, name='naari_shakti'),
    path('naari_shakti/bihar', views.naari_shakti_bihar, name='naari_shakti_bihar'),
    path('naari_shakti/rajasthan', views.naari_shakti_rajasthan, name='naari_shakti_rajasthan'),
    path('naari_shakti/meerut', views.naari_shakti_meerut, name='naari_shakti_meerut'),
    path('naari-shakti-bihar/donations/', views.naari_shakti_bihar_donations, name='naari_shakti_bihar_donations'),
    path('naari-shakti-rajasthan/donations/', views.naari_shakti_rajasthan_donations, name='naari_shakti_rajasthan_donations'),
    path('naari-shakti-meerut/donations/', views.naari_shakti_meerut_donations, name='naari_shakti_meerut_donations'),
    path('naari-shakti-india/donations/', views.naari_shakti_india_donations, name='naari_shakti_india_donations'),
    path("myfirstkick", views.myfirstkick_page, name="myfirstkick_page"),
    # ===== misc =====
    path('anant_login', views.student_login, name='student_login'),
    path('scoutingasservice', views.scoutingasservice, name='scoutingasservice'),
    path('scoutingcommunity', views.scoutingcommunity, name='scoutingcommunity'),
    path('scoutingatschools', views.scoutingatschools, name='scoutingatschools'),
    path('career360becomepartner', views.career360becomepartner, name='career360becomepartner'),
    path('partner_ecosystem', views.career360faq, name='career360faq'),
    path('career360fieldofdreams', views.career360fieldofdreams, name='career360fieldofdreams'),
    path('IKF_Partnership_Guidelines', views.career360impactinaction, name='career360impactinaction'),
    path('parent_sop', views.career360parentsplayers, name='career360parentsplayers'),
    path('parent-conversation/', views.parent_conversation_quiz, name='parent_conversation_quiz'),
    path('parent-conversation/submit/', views.parent_conversation_submit, name='parent_conversation_submit'),
    path('parent-conversation/responses/', views.parent_conversation_responses, name='parent_conversation_responses'),
    path('ikf-for-players', views.ikf_for_players, name='ikf_for_players'),
    path('ikf-for-parents', views.ikf_for_parents, name='ikf_for_parents'),
    path('ikf-for-donors', views.ikf_for_donors, name='ikf_for_donors'),
    path('ikf-for-scouts', views.ikf_for_scouts, name='ikf_for_scouts'),
    path('ikf360vision', views.career360vision, name='career360vision'),
    # ── IKF 360 persona sub-pages ──
    path('ikf-360/player', views.ikf360_player, name='ikf360_player'),
    path('ikf-360/parent', views.ikf360_parent, name='ikf360_parent'),
    path('ikf-360/career', views.ikf360_career, name='ikf360_career'),
    path('ikf-360/partner', views.ikf360_partner, name='ikf360_partner'),
    path('ikf-360/supporter', views.ikf360_supporter, name='ikf360_supporter'),
    path('IkfTrials', views.season5landing, name='IkfTrials'),
    path("scouted-players/", views.scouted_players, name="scouted_players"),
    path('season6', views.season5, name='season5'),
    path('valueforfee', views.workshopfee, name='workshopfee'),
    path('ikfinnews', views.news_homepage, name='ikfinnews'),
    path('dashboard', views.dashboard_view, name='dashboard'),
    path('get_workshopinfo', views.get_workshopinfo, name='get_workshopinfo'),
    path('calendar_partial/', views.calendar_partial, name='calendar_partial'),
    path('faces', views.faces, name='faces'),
    path('submit-contact-form/', views.submit_contact_form, name='submit_contact_form'),
    path("privacy/", views.privacy, name="privacy"),
    
    path('rep/onboard/<str:token>/', views.rep_onboarding, name='rep_onboarding'),
    path('rep/preview/<str:token>/', views.rep_preview, name='rep_preview'),
    path('rep/become-partner/', views.rep_become_partner, name='rep_become_partner'),
    path("<slug:code>/", views.message_weblink, name="message_weblink"),
    
    path('rep/<slug:slug>/', views.rep_public, name='rep_public'),
    
    path("sitemap", views.sitemap_view, name="sitemap"),
    path('termsandconditions', views.terms_and_conditions, name='terms_and_conditions'),
    path("noticeboard/upcoming-trials", views.upcoming_trials_page, name="upcoming_trials_page"),

    path('parent-fuelling-ikf', views.parent_fuelling_ikf, name='parent-fuelling-ikf'),

    # AJAX endpoints (names MUST match template)
    path("api/upcoming-trials/filters/", views.upcoming_trials_filters_api, name="upcoming_trials_filters_api"),
    path("api/upcoming-trials/cities/", views.upcoming_trials_cities_api, name="upcoming_trials_cities_api"),
    path("api/upcoming-trials/city/", views.upcoming_trials_city_api, name="upcoming_trials_city_api"),
    path("api/upcoming-trials/last-modified/", views.upcoming_trials_last_modified, name="upcoming_trials_last_modified"),
   

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
