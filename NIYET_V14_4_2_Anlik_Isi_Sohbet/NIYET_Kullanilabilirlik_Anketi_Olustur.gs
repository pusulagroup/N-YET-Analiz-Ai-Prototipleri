function createNiyetUsabilityTestForm() {
  var form = FormApp.create('NİYET Kullanılabilirlik Testi – V14.3 TEST');
  form.setDescription(
    'Bu çalışma NİYET prototipinin kullanılabilirliğini değerlendirmek için hazırlanmıştır. ' +
    'Amaç, arayüzde zorlanılan noktaları, anlaşılması güç kavramları, bekleme sürelerini ve en beğenilen özellikleri belirlemektir. ' +
    'Ad, soyad ve e-posta istenmez. Lütfen görevleri tamamladıktan sonra gerçek deneyiminize göre yanıt verin.'
  );
  form.setCollectEmail(false);
  form.setProgressBar(true);
  form.setShuffleQuestions(false);
  form.setConfirmationMessage('Teşekkürler. Yanıtların NİYET prototipinin kullanıcı deneyimini geliştirmek için kullanılacaktır.');

  // Gönüllülük
  form.addCheckboxItem()
    .setTitle('Katılım onayı')
    .setHelpText('Bu test gönüllüdür. Kimlik bilgisi istenmez ve yanıtlar yalnızca proje geliştirme/değerlendirme amacıyla kullanılacaktır.')
    .setChoiceValues(['Gönüllü olarak katılıyorum.'])
    .setRequired(true);

  form.addSectionHeaderItem().setTitle('1. Katılımcı Profili');

  form.addMultipleChoiceItem()
    .setTitle('Yaş grubunuz')
    .setChoiceValues([
      '18 yaşından küçüğüm',
      '18–24',
      '25–34',
      '35–49',
      '50 ve üzeri'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Günde yaklaşık ne kadar sosyal medya kullanıyorsunuz?')
    .setChoiceValues([
      '1 saatten az',
      '1–2 saat',
      '2–4 saat',
      '4 saatten fazla'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Yeni bir uygulamayı veya dijital arayüzü öğrenme konusunda kendinizi nasıl değerlendirirsiniz?')
    .setChoiceValues([
      'Zorlanırım',
      'Biraz zorlanırım',
      'Orta',
      'Kolay öğrenirim',
      'Çok kolay öğrenirim'
    ])
    .setRequired(true);

  form.addSectionHeaderItem()
    .setTitle('2. Test Görevleri')
    .setHelpText(
      'Görevleri sırayla uygulayın:\n' +
      '1) Akıştan bir kullanıcı profiline girip geri dönün.\n' +
      '2) Profilinizde bir mesaj yazın, niyet seçin ve NİYET ile analiz edin.\n' +
      '3) Öneri çıkarsa “Değişikliği uygula ve paylaş” akışını deneyin.\n' +
      '4) Bir gönderiye yorum yapıp Tartışma Isısı ve varsa Bağlam Etkisini inceleyin.\n' +
      '5) Bir kullanıcıyla en az iki mesajlık sohbet yapıp Sohbet Sağlığını ve profilinizde Sohbet Genel skorunu bulun.\n' +
      '6) NİYET ekranından genel skoru ve en düşük ana alanı bulun.'
    );

  var taskChoices = [
    'Yardım almadan tamamladım',
    'Küçük bir yardımla tamamladım',
    'Tamamlayamadım – ne yapacağımı anlayamadım',
    'Tamamlayamadım – teknik hata oluştu'
  ];

  addTaskQuestion_(form, 'Görev 1 – Profil açma ve ana akışa geri dönme', taskChoices);
  addTaskQuestion_(form, 'Görev 2 – Paylaşım oluşturma, niyet seçme ve NİYET analizi', taskChoices);
  addTaskQuestion_(form, 'Görev 3 – Minimum Müdahale / “Değişikliği uygula ve paylaş”', taskChoices);
  addTaskQuestion_(form, 'Görev 4 – Yorum, Tartışma Isısı ve varsa Bağlam Etkisi', taskChoices);
  addTaskQuestion_(form, 'Görev 5 – Özel sohbet, Sohbet Sağlığı ve Sohbet Genel skoru', taskChoices);
  addTaskQuestion_(form, 'Görev 6 – NİYET Skoru ve en düşük ana alanı bulma', taskChoices);

  form.addGridItem()
    .setTitle('Aşağıdaki bölümleri kullanmak ne kadar kolaydı?')
    .setRows([
      'Profil ve gezinme',
      'Paylaşım oluşturma',
      'NİYET analiz sonuçlarını anlama',
      'Minimum Müdahale önerileri',
      'Yorum ve Tartışma Isısı',
      'Özel sohbet',
      'NİYET Skoru ekranı'
    ])
    .setColumns(['1 – Çok zor', '2', '3 – Orta', '4', '5 – Çok kolay'])
    .setRequired(true);

  form.addSectionHeaderItem().setTitle('3. Süre ve Hız Deneyimi');

  form.addMultipleChoiceItem()
    .setTitle('Tüm test görevlerini tamamlamanız yaklaşık ne kadar sürdü?')
    .setChoiceValues([
      '5 dakikadan az',
      '5–10 dakika',
      '11–15 dakika',
      '16–20 dakika',
      '20 dakikadan fazla'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Bir paylaşım için NİYET analizinin ilk ana sonuçları yaklaşık ne kadar sürede geldi?')
    .setChoiceValues([
      '5 saniye veya daha az',
      '6–10 saniye',
      '11–20 saniye',
      '21–40 saniye',
      '40 saniyeden fazla',
      'Analiz çalışmadı / ölçemedim'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Algı Kararlılığı ve Minimum Müdahale önerilerinin tamamlanması yaklaşık ne kadar sürdü?')
    .setChoiceValues([
      '5 saniye veya daha az',
      '6–10 saniye',
      '11–20 saniye',
      '21–40 saniye',
      '40 saniyeden fazla',
      'Öneri çıkmadı / ölçemedim'
    ])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('Sohbet botunun yanıt vermesi genellikle ne kadar sürdü?')
    .setChoiceValues([
      '5 saniye veya daha az',
      '6–10 saniye',
      '11–20 saniye',
      '21–40 saniye',
      '40 saniyeden fazla',
      'Sohbet çalışmadı / ölçemedim'
    ])
    .setRequired(true);

  form.addScaleItem()
    .setTitle('Bekleme süreleri genel kullanıcı deneyiminizi ne kadar olumsuz etkiledi?')
    .setBounds(1, 5)
    .setLabels('1 – Hiç etkilemedi', '5 – Çok olumsuz etkiledi')
    .setRequired(true);

  form.addSectionHeaderItem().setTitle('4. Anlaşılabilirlik ve Zorlanılan Noktalar');

  form.addMultipleChoiceItem()
    .setTitle('Sizce NİYET’in temel amacı hangisidir?')
    .setChoiceValues([
      'Kullanıcının ne paylaşabileceğine karar vermek',
      'Kullanıcının niyeti ile okuyucunun olası algısı arasındaki farkı görünür kılıp iletişim geri bildirimi vermek',
      'Sadece küfür ve hakaret tespit etmek',
      'Paylaşımların ne kadar popüler olacağını tahmin etmek'
    ])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('En anlaşılması güç bulduğunuz kavram veya göstergeler hangileriydi?')
    .setChoiceValues([
      'Niyet–Algı Uyumu',
      'Muhtemel Okuyucu Algısı',
      'Yanlış Anlaşılma Riski',
      'Tartışma Yaratma İhtimali',
      'Algı Kararlılığı',
      'Minimum Müdahale / Algı Kazancı',
      'Tartışma Isısı',
      'Bağlam Etkisi (Gölge Niyet)',
      'Sohbet Sağlığı',
      'Sohbet Genel Skoru',
      'NİYET Skoru',
      'Hiçbiri'
    ])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('Kullanım sırasında en çok zorlandığınız bölümler hangileriydi?')
    .setChoiceValues([
      'Profil/ekranlar arasında gezinme',
      'Paylaşım oluşturma',
      'Niyet seçimi',
      'NİYET analizini başlatma',
      'Analiz sonucunu yorumlama',
      'Minimum Müdahale önerisini uygulama',
      'Yorum yazma',
      'Tartışma Isısını anlama',
      'Özel sohbet',
      'NİYET Skorunu bulma/anlama',
      'Hiçbiri'
    ])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('En çok zorlandığınız veya duraksadığınız yeri kendi cümlenizle anlatır mısınız?')
    .setRequired(true);

  form.addSectionHeaderItem().setTitle('5. Beğenilen Özellikler ve Genel Değerlendirme');

  form.addCheckboxItem()
    .setTitle('En çok beğendiğiniz özellikler hangileriydi?')
    .setChoiceValues([
      'Niyet–Algı Analizi',
      'Yanlış Anlaşılma Riski',
      'Tartışma Yaratma İhtimali',
      'Algı Kararlılığı',
      'Minimum Müdahale önerileri',
      'Tartışma Isısı',
      'Bağlam Etkisi (Gölge Niyet)',
      'Sohbet Sağlığı',
      'Genç/Korumalı Mod',
      'NİYET Skoru ve gelişim ekranı',
      'Sosyal medya arayüzü / genel tasarım'
    ])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('En çok beğendiğiniz özelliği neden beğendiniz?')
    .setRequired(false);

  form.addScaleItem()
    .setTitle('NİYET’in ne yaptığını genel olarak anlamak ne kadar kolaydı?')
    .setBounds(1, 5)
    .setLabels('1 – Çok zor', '5 – Çok kolay')
    .setRequired(true);

  form.addScaleItem()
    .setTitle('Arayüz genel olarak ne kadar kullanışlıydı?')
    .setBounds(1, 5)
    .setLabels('1 – Çok kullanışsız', '5 – Çok kullanışlı')
    .setRequired(true);

  form.addScaleItem()
    .setTitle('Bu özelliği gerçek bir sosyal medya platformunda kullanmak ister miydiniz?')
    .setBounds(1, 5)
    .setLabels('1 – Kesinlikle istemezdim', '5 – Kesinlikle isterdim')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('18 yaş altı Korumalı Modun koyu gri arka planla ayrılması sizce fark edilir miydi?')
    .setChoiceValues([
      'Evet, açıkça fark edildi',
      'Biraz fark edildi',
      'Hayır, yeterince fark edilmedi',
      'Bu modu test etmedim'
    ])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('NİYET’te tek bir şeyi değiştirebilseydiniz neyi değiştirirdiniz?')
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('Test sırasında yaşadığınız teknik hata varsa kısaca yazın. Yoksa “Yok” yazabilirsiniz.')
    .setRequired(true);

  // Yanıtları otomatik bir Google Sheet'e bağla.
  var sheet = SpreadsheetApp.create('NİYET Kullanılabilirlik Testi – Yanıtlar');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, sheet.getId());

  Logger.log('FORM DÜZENLEME LİNKİ: ' + form.getEditUrl());
  Logger.log('FORM KATILIM LİNKİ: ' + form.getPublishedUrl());
  Logger.log('YANITLAR SHEET: ' + sheet.getUrl());
}

function addTaskQuestion_(form, title, choices) {
  form.addMultipleChoiceItem()
    .setTitle(title)
    .setChoiceValues(choices)
    .setRequired(true);
}
