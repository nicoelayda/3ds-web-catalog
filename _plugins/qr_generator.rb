require 'rqrcode_png'

module Jekyll

  class QrCodeTag < Liquid::Tag
    def initialize(tag_name, url, tokens)
      super
      @url = url.strip
    end

    def lookup(context, name)
      lookup = context
      name.split(".").each { |value| lookup = lookup[value] }
      lookup
    end

    def render(context)
      page_url = "#{lookup(context, 'site.url')}#{context[@url]}"
      qr = RQRCode::QRCode.new(page_url) # Size increased because URLs can be long
      png = qr.to_img.resize(300, 300)

      <<-MARKUP.strip
      <div class="qrcode">
        <img src="#{png.to_data_url}" alt="#{page_url}">
      </div>
      MARKUP
    end
  end

end

Liquid::Template.register_tag('qr', Jekyll::QrCodeTag)