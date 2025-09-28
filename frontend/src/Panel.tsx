// Import for type checking
import {
  checkPluginVersion,
  type InvenTreePluginContext
} from '@inventreedb/ui';
import { Tabs } from '@mantine/core';
import * as DXF from 'dxf';
import parse from 'html-react-parser';
import { useEffect, useState } from 'react';

function DXFImage({ contents }: { contents: string } & {}) {
  if (!contents) return <></>;

  const helper = new DXF.Helper(contents);

  const svg = helper.toSVG();

  return <>{parse(svg)}</>;
}

/**
 * Render a custom panel with the provided context.
 * Refer to the InvenTree documentation for the context interface
 * https://docs.inventree.org/en/latest/plugins/mixins/ui/#plugin-context
 */
function DXFViewerPanel({ context }: { context: InvenTreePluginContext }) {
  const [image_datas, setImageDatas] = useState<string[]>([]);

  const attachment_urls: string[] = context.context.attachments;

  useEffect(() => {
    Promise.all(
      attachment_urls.map(
        (url) =>
          new Promise<string>((resolve) => {
            fetch(url).then((response) => {
              response.text().then((text) => {
                resolve(text);
              });
            });
          })
      )
    ).then(setImageDatas);
  }, [attachment_urls]);

  const tab_list = attachment_urls.map((url) => (
    <Tabs.Tab value={url.substring(url.lastIndexOf('/') + 1)}>
      {url.substring(url.lastIndexOf('/') + 1)}
    </Tabs.Tab>
  ));

  const tab_panels = attachment_urls.map((url, index) => (
    <Tabs.Panel value={url.substring(url.lastIndexOf('/') + 1)}>
      <DXFImage contents={image_datas[index]} />
    </Tabs.Panel>
  ));

  return (
    <>
      <Tabs>
        <Tabs.List>{tab_list}</Tabs.List>
        {tab_panels}
      </Tabs>
    </>
  );
}

// This is the function which is called by InvenTree to render the actual panel component
export function renderDXFViewerPanel(context: InvenTreePluginContext) {
  checkPluginVersion(context);

  return <DXFViewerPanel context={context} />;
}
